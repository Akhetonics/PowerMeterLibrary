import serial
import time
import struct 
import serial.tools.list_ports

from commands import Commands
from helpers import convert_number_to_wavelength, extract_number

class DeviceController:
    def __init__(self, dataProcessingStrategies=[]):
        self.optical_power = None
        self.reference_power = None
        self.adc_value = None
        self.frequency = None
        self.power_adjustment_gear = None
        self.mode = None
        self.wavelength = None
        self.battery_level = None
        self.data_processing_strategies = dataProcessingStrategies
    
    def __enter__(self):
        self._connect_to_device()
        return self
    
    def __exit__ (self, exc_type, exc_val, exc_tb):
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
                if len(received_data) == 13:
                    print(f"Successful response from port: {port.device}")
                    return port.device
            except serial.SerialException as e:
                print(f"Error connecting to port {port.device}: {e}")
        print("No proper response received from any port.")
        return None
    
    def _connect_to_device(self, timeout_seconds=60):
        start_time = time.time()
        port = None
        while port is None:
            if time.time() - start_time > timeout_seconds:
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

    def _validate_data(self, data, expected_function_nr, expected_function_sub_nr):
        if data is None or len(data) != 13:
            raise DataLengthError("Error: Did not receive enough data.")
        
        start_byte = extract_number(data, 0, 1)
        if start_byte != 0xAA:
            raise StartByteError("Error: Start byte is wrong - device is not compatible.")
        
        function_nr = extract_number(data, 1, 2)
        if function_nr != expected_function_nr:
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

    def send_command(self, command):
        if isinstance(command, Commands):
            command_to_send = command.value
        else:
            command_to_send = command
        self.send_data(command_to_send)
        data = self.receive_data()
        return data
    
    def get_optical_power_measurement_result(self):
        return self.send_command("return_optical_power_measurement_result")

    def switch_wavelength_gear_and_read_reference_power(self):
        return self.send_command("switch_wavelength_gear_and_read_reference_power")

    def switch_wavelength_gear_directly(self):
        return self.send_command("switch_wavelength_gear_directly")

    def switch_optical_power_unit_to_uw(self):
        return self.send_command("switch_optical_power_unit_to_uw")

    def switch_optical_power_unit_to_dbm(self):
        return self.send_command("switch_optical_power_unit_to_dbm")

    def switch_to_view_reference_value_mode(self):
        return self.send_command("switch_to_view_reference_value_mode")

    def set_current_optical_power_as_reference(self):
        return self.send_command("set_current_optical_power_as_reference")

    def switch_led_backlight_off(self):
        return self.send_command("switch_led_backlight_off")

    def turn_on_led_backlight(self):
        return self.send_command("turn_on_led_backlight")

    def turn_off_led_backlight(self):
        return self.send_command("turn_off_led_backlight")

    def auto_power_off(self):
        return self.send_command("auto_power_off")

    def automatic_shutdown_on(self):
        return self.send_command("automatic_shutdown_on")

    def reset_optical_power_reference_value(self):
        return self.send_command("reset_optical_power_reference_value")

    def delete_all_records_of_eeprom(self):
        return self.send_command("delete_all_records_of_eeprom")

    def returns_the_number_of_stored_power_records(self):
        return self.send_command("returns_the_number_of_stored_power_records")

    def clear_stored_power_records(self):
        return self.send_command("clear_stored_power_records")

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

