import asyncio
import serial
import time
import serial.tools.list_ports

from DataProcessingStrategies.StrategyLoader import DataProcessingStrategyLoader
from commands import CommandTypes, Commands
from helpers import extract_number

class DeviceController:
    def __init__(self, connectionTimeout = 60, backlight_enabled = True):
        self.optical_power = None
        self.reference_power = None
        self.adc_value = None
        self.frequency = None
        self.power_adjustment_gear = None
        self.mode = None
        self.wavelength = None
        self.battery_level = None
        self.do_print_data = False
        self.device_response_time = 0
        self._data_processing_strategies = DataProcessingStrategyLoader("DataProcessingStrategies" , "DataProcessingStrategy").strategies # load all response processing strategies from folder
        self._connection_timeout = connectionTimeout
        self._is_display_settings_changed = None
        self._is_power_data_received = None
        self._update_stop_event = asyncio.Event()
        self._update_stop_event.set()
        self._update_task = None
        self._backlight_enabled = backlight_enabled
        self._command_variation = 0 # in the update function it loops from 0 to 2 to use the 3 different power fetching commands
        self._buffer = bytearray()  # Persistent buffer to accumulate data
        self._expected_length = 13
    
    @property
    def optical_power(self):
        return self._optical_power

    @optical_power.setter
    def optical_power(self, value):
        self._optical_power = value
        self._is_power_data_received = True  # set that variable to true to mark that a value has been received - in case we want to wait for this specific value

    async def __aenter__(self):
        await self._connect_to_device()
        if(self._backlight_enabled):
            await self.turn_on_backlight(True)
        return self
    
    async def __aexit__ (self, exc_type, exc_val, exc_tb):
        if(self._backlight_enabled):
            await self.turn_on_backlight(False)
        self._close_serial_port()
        return False
    
    def start_update_in_background(self):
        if self._update_task is None or self._update_task.done():
            # Zurücksetzen des Stop-Events, um die Schleife in `update` laufen zu lassen
            self._update_stop_event.clear()
            self._update_task = asyncio.create_task(self.update_looped())

    async def stop_update(self):
        # Setzt das Event, um die Schleife in `update` zu stoppen
        self._update_stop_event.set()
        if self._update_task:
            # Warte auf die Beendigung der aktuellen Ausführung von `update`
            await self._update_task
            self._update_task = None

    async def update_looped(self):
        while not self._update_stop_event.is_set():
            await self.update()
            await asyncio.sleep(0.001)

    async def update(self):
        start_time = time.perf_counter()
        self._command_variation = (self._command_variation +1) % 3
        # fetch the power but use a variety of those commands to get the additional data as well like battery power, reference power etc.
        if self._command_variation == 0:
            self.send_command(Commands.RETURN_POWER_WAVELENGTH_BATTERY)
        elif self._command_variation == 1:
            self.send_command(Commands.RETURN_POWER_ADC_FREQUENCY)
        elif self._command_variation == 2:
            self.send_command(Commands.RETURN_POWER_REFERENCE_POWER)
        await self.wait_for_power_data_change(2)
        end_time = time.perf_counter()
        self.device_response_time = (end_time - start_time) *1000
        if(self.do_print_data == True):
            print(f"{(self.device_response_time):.2f} ms > power: {self.optical_power} \t λ: {self.wavelength} \t🔋 {self.battery_level} \tADC: {self.adc_value} \t ref_pwr: {self.reference_power} ")

    async def turn_on_backlight(self, is_turn_on = True):
        if(is_turn_on == True):
            command = Commands.TURN_ON_LED_BACKLIGHT
        else:
            command = Commands.TURN_OFF_LED_BACKLIGHT
        self.send_command(command)
        if await self.wait_for_display_settings_change(0.25) == False: # send again if timeout occured
            self.send_command(command)

    async def _find_device_port(self):
        available_ports = serial.tools.list_ports.comports()
        for port in available_ports:
            
            print(f"Trying port: {port.device}")
            try:
                ser = serial.Serial(port.device, 9600, timeout=1)
                ser.write(Commands.RETURN_POWER_ADC_FREQUENCY.value)  # Send command
                await asyncio.sleep(0.3)
                if ser.in_waiting < 13:
                    ser.close()
                    continue
                received_data = ser.read(13)  # Read response
                ser.close()  # Close the serial connection
                if self._validate_data(received_data , CommandTypes.POWER_REQUEST.value , 0x00):
                    print(f"Successful response from port: {port.device}")
                    return port.device
            except serial.SerialException as e:
                print(f"Error connecting to port {port.device}: {e}")
            except DataValidationError as data_ex:
                print(f"could not read data from port {port.device}: {data_ex}")
        print("No proper response received from any port.")
        return None

    async def _connect_to_device(self):
        start_time = time.time()
        port = None
        while port is None:
            if time.time() - start_time > self._connection_timeout:
                print("Connection timeout.")
                break
            port = await self._find_device_port()
            if port:
                self.ser = serial.Serial(port, 9600, timeout=1)
                print(f"Connected to device on port: {port}")
                break
            else:
                print("Device not found, retrying...")
                await asyncio.sleep(0.5)

    def _close_serial_port(self):
        if self.ser is not None:
            self.ser.close()

    def _validate_data(self, data, command_type, expected_function_sub_nr):
        if data is None or len(data) < 13:
            raise DataLengthError(f"Error: Did not receive enough data. only got: {len(data)} >> {data}")
        
        start_byte = extract_number(data, 0, 1)
        if start_byte != 0xAA:
            raise StartByteError(f"Error: Start byte is wrong - device is not compatible. >> {data}")
        
        command_type = extract_number(data, 1, 2)
        if command_type != command_type:
            raise FunctionNumberError(f"Error: {command_type.__name__} is not what was expected. >> {data}")
        
        function_sub_nr = extract_number(data, 2, 3)
        if function_sub_nr != expected_function_sub_nr:
            raise FunctionSubNumberError("Error: Function sub number is not what was expected.")
        
        # if there are no exeptions until here, then the data set is valid
        return True
    
    def send_data(self, data):
        self.ser.write(data)  # Send data

    def _apply_strategy(self, data):
        function_nr = extract_number(data, 1, 2)
        function_sub_id = extract_number(data, 2, 3)

        # search for the proper startegy for that data
        for strategy in self._data_processing_strategies:
            if strategy.applies_to(function_nr, function_sub_id):
                strategy.process_data(self, data)
                return True
        return False  # no matching strategy was found
    
    def receive_data(self):
        # Read available data without blocking
        bytes_to_read = self.ser.in_waiting
        if bytes_to_read:
            data = self.ser.read(bytes_to_read)
            self._buffer.extend(data)

        # Check if we have enough data to process
        if len(self._buffer) >= self._expected_length:
            # Process data here
            data_to_process = self._buffer[:self._expected_length]
            if not self._apply_strategy(data_to_process):
                print("could not find a proper strategy for this data block", data_to_process)
            # Remove processed data from buffer
            del self._buffer[:self._expected_length]

        # Optionally, you can return whether data was processed
        return None

    # one can use the command-enum or its value to send the command.
    def send_command(self, command: Commands):
        command_type = extract_number( command.value,1,2)
        if command_type == CommandTypes.POWER_REQUEST.value:
            self._is_power_data_received = False
        if command_type == CommandTypes.DISPLAY_SETTINGS_CHANGE.value:
            self._is_display_settings_changed = False

        self.send_data(command.value)
        
    async def wait_for_display_settings_change(self, timeout=2) -> bool:
        """
        Waits until `self.display_settings_changed` becomes True or the timeout expires.

        :param timeout: Maximum time to wait in seconds.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.receive_data()
            if self._is_display_settings_changed:
                self._is_display_settings_changed = False
                return True
            await asyncio.sleep(0.01)  # Sleep for 10 milliseconds before checking again
        else:
            return False
    
    async def wait_for_power_data_change(self, timeout=2) -> bool:
        """
        Waits until `self.power_data_received` becomes True or the timeout expires.

        :param timeout: Maximum time to wait in seconds.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.receive_data()
            if self._is_power_data_received:
                self._is_power_data_received = False
                return True
            await asyncio.sleep(0.01)  # Sleep for 10 milliseconds before checking again
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

