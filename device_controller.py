import serial
import time
import struct 
import serial.tools.list_ports

from commands import CommandTypes, Commands
from helpers import convert_number_to_wavelength, extract_number

class DeviceController:
    def __init__(self, dataProcessingStrategies, connectionTimeout = 60):
        self.optical_power = None
        self.reference_power = None
        self.adc_value = None
        self.frequency = None
        self.power_adjustment_gear = None
        self.mode = None
        self.wavelength = None
        self.battery_level = None
        self.data_processing_strategies = dataProcessingStrategies
        self.connection_timeout = connectionTimeout
        self.display_settings_changed = None
        self.power_data_received = None
    
    @property
    def optical_power(self):
        return self._optical_power

    @optical_power.setter
    def optical_power(self, value):
        self._optical_power = value
        self.power_data_received = True  # set that variable to true to mark that a value has been received - in case we want to wait for this specific value

    def __enter__(self):
        self._connect_to_device()
        return self
    
    def __exit__ (self, exc_type, exc_val, exc_tb):
        self.send_command(Commands.TURN_OFF_LED_BACKLIGHT)
        if self.wait_for_display_settings_change(0.25) == False: # send again if timeout occured
            self.send_command(Commands.TURN_OFF_LED_BACKLIGHT)
        self._close_serial_port()
        return False

    def _find_device_port(self):
        available_ports = serial.tools.list_ports.comports()
        for port in available_ports:
            print(f"Trying port: {port.device}")
            try:
                ser = serial.Serial(port.device, 9600, timeout=1)
                ser.write(Commands.RETURN_POWER_ADC_FREQUENCY.value)  # Send command
                time.sleep(0.1)  # Wait for response
                received_data = ser.read(13)  # Read response
                ser.close()  # Close the serial connection
                if self._validate_data(received_data , CommandTypes.POWER_REQUEST.value , 0x00):
                    print(f"Successful response from port: {port.device}")
                    return port.device
            except serial.SerialException as e:
                print(f"Error connecting to port {port.device}: {e}")
        print("No proper response received from any port.")
        return None
    
    def _connect_to_device(self):
        start_time = time.time()
        port = None
        while port is None:
            if time.time() - start_time > self.connection_timeout:
                print("Connection timeout.")
                break
            port = self._find_device_port()
            if port:
                self.ser = serial.Serial(port, 9600, timeout=1)
                print(f"Connected to device on port: {port}")
                break
            else:
                print("Device not found, retrying...")
                time.sleep(1)

    def _close_serial_port(self):
        if self.ser is not None:
            self.ser.close()

    def _validate_data(self, data, command_type, expected_function_sub_nr):
        if data is None or len(data) != 13:
            raise DataLengthError("Error: Did not receive enough data.")
        
        start_byte = extract_number(data, 0, 1)
        if start_byte != 0xAA:
            raise StartByteError("Error: Start byte is wrong - device is not compatible.")
        
        function_nr = extract_number(data, 1, 2)
        if function_nr != command_type:
            raise FunctionNumberError("Error: Function number is not what was expected.")
        
        function_sub_id = extract_number(data, 2, 3)
        if function_sub_id != expected_function_sub_nr:
            raise FunctionSubNumberError("Error: Function sub number is not what was expected.")
        
        # if there are no exeptions until here, then the data set is valid
        return True
    
    def send_data(self, data):
        self.ser.write(data)  # Send data

    def _apply_strategy(self, data):
        function_nr = extract_number(data, 1, 2)
        function_sub_id = extract_number(data, 2, 3)

        # search for the proper startegy for that data
        for strategy in self.data_processing_strategies:
            if strategy.applies_to(function_nr, function_sub_id):
                strategy.process_data(self, data)
                return True
        return False  # no matching strategy was found
    
    def receive_data(self):
        if self.ser.in_waiting < 13: # there is bytes available - we assume, that the first byte is the startbyte 0xAA - to simplify the matter 
            return None
        data = self.ser.read(13)
        if not self._apply_strategy(data):
            print("could not find a proper strategy for this data block" , data)

    # one can use the command-enum or its value to send the command.
    def send_command(self, command: Commands):
        command_type = extract_number( command.value,1,2)
        if command_type == CommandTypes.POWER_REQUEST.value:
            self.power_data_received = False
        if command_type == CommandTypes.DISPLAY_SETTINGS_CHANGE.value:
            self.display_settings_changed = False

        self.send_data(command.value)
        time.sleep(0.01) # sleep for 10 milliseconds
        
    def wait_for_display_settings_change(self, timeout=2) -> bool:
        """
        Waits until `self.display_settings_changed` becomes True or the timeout expires.

        :param timeout: Maximum time to wait in seconds.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.receive_data()
            if self.display_settings_changed:
                self.display_settings_changed = False
                return True
            time.sleep(0.01)  # Sleep for 10 milliseconds before checking again
        else:
            return False
    
    def wait_for_power_data_change(self, timeout=2) -> bool:
        """
        Waits until `self.power_data_received` becomes True or the timeout expires.

        :param timeout: Maximum time to wait in seconds.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.receive_data()
            if self.power_data_received:
                self.power_data_received = False
                return True
            time.sleep(0.01)  # Sleep for 10 milliseconds before checking again
        else:
            return False
        
class DataValidationError(Exception):
    pass

class DataLengthError(DataValidationError):
    pass

class StartByteError(DataValidationError):
    pass

class FunctionNumberError(DataValidationError):
    pass

class FunctionSubNumberError(DataValidationError):
    pass

