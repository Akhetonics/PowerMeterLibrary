import serial
import time
import struct 
import serial.tools.list_ports

class DeviceController:
    # Define the commands based on the protocol from the image
    commands = {
        "return_current_optical_power": b'\xAA\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "return_current_optical_power_reference": b'\xAA\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "return_optical_power_measurement_result": b'\xAA\x11\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "switch_wavelength_gear_and_read_reference_power": b'\xAA\x21\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "switch_wavelength_gear_directly": b'\xAA\x21\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "switch_optical_power_unit_to_uw": b'\xAA\x22\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "switch_optical_power_unit_to_dbm": b'\xAA\x22\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "switch_to_view_reference_value_mode": b'\xAA\x23\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "set_current_optical_power_as_reference": b'\xAA\x23\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "switch_led_backlight_off": b'\xAA\x24\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "turn_on_led_backlight": b'\xAA\x24\x41\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "turn_off_led_backlight": b'\xAA\x24\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "auto_power_off": b'\xAA\x37\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "automatic_shutdown_on": b'\xAA\x37\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "reset_optical_power_reference_value": b'\xAA\x50\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "delete_all_records_of_eeprom": b'\xAA\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "read_the_value_of_corresponding_address_of_eeprom": b'\xAA\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',  # Placeholder, needs the specific address to read from
        "returns_the_number_of_stored_power_records": b'\xAA\x26\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        "clear_stored_power_records": b'\xAA\x19\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    }

    def find_device_port(self):
        available_ports = serial.tools.list_ports.comports()
        for port in available_ports:
            print(f"Trying port: {port.device}")
            try:
                ser = serial.Serial(port.device, 9600, timeout=1)
                ser.write(self.commands["return_current_optical_power"])  # Send command
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
    
    def connect_to_device(self, timeout_seconds=60):
        start_time = time.time()
        port = None
        while port is None:
            if time.time() - start_time > timeout_seconds:
                print("Connection timeout.")
                break
            port = self.find_device_port()
            if port:
                self.ser = serial.Serial(port, 9600, timeout=1)
                print(f"Connected to device on port: {port}")
                break
            else:
                print("Device not found, retrying...")
                time.sleep(1)
    def close_serial_port(self):
        self.ser.close()
        
    def extract_number(self, data, start, end):
        # Determine the number of bytes
        num_bytes = end - start
        
        # Choose the appropriate format specifier based on the number of bytes
        format_specifier = {1: 'B', 2: 'H', 4: 'I'}.get(num_bytes)
        if format_specifier is None:
            raise ValueError("Unsupported number of bytes")
        
        # Unpack the data using the chosen format specifier
        extracted_value = struct.unpack('>' + format_specifier, data[start:end])[0]
        return extracted_value

    def validate_data(self, data, expected_function_nr, expected_function_sub_nr):
        if data is None or len(data) != 13:
            raise DataLengthError("Error: Did not receive enough data.")
        
        start_byte = self.extract_number(data, 0, 1)
        if start_byte != 0xAA:
            raise StartByteError("Error: Start byte is wrong - device is not compatible.")
        
        function_nr = self.extract_number(data, 1, 2)
        if function_nr != expected_function_nr:
            raise FunctionNumberError("Error: Function number is not what was expected.")
        
        function_sub_id = self.extract_number(data, 2, 3)
        if function_sub_id != expected_function_sub_nr:
            raise FunctionSubNumberError("Error: Function sub number is not what was expected.")
        
        # if there are no exeptions until here, then the data set is valid
        return True
            
    def send_data(self, data):
        self.ser.write(data)  # Send data
        time.sleep(0.1)  # Short pause to ensure all data is transmitted

    def receive_data(self ):
        data = self.ser.read(14)  # Receive 13 bytes of data
        return data

    def send_command(self, command):
        self.send_data(self.commands[command])
        data = self.receive_data()
        return data

    def get_current_optical_power(self):
        data = self.send_command("return_current_optical_power")
        optical_power = self.extract_number(data,5,9)
        adc_value = self.extract_number(data,9,11)
        frequency = adc_value = self.extract_number(data,11,12)
        power_adjustment_gear = adc_value = self.extract_number(data,12,13)
        print ( f"power meassured: {optical_power}  adc {adc_value} freq {frequency} pwr_gear {power_adjustment_gear}")
        return (optical_power , adc_value , frequency , power_adjustment_gear)

    def get_current_optical_power_reference(self):
        data = self.send_command("return_current_optical_power_reference")
        optical_power = self.extract_number(data,5,9)
        mode = self.extract_number(data,9,10)
        wavelength = adc_value = self.extract_number(data,11,12)
        batteryLevel = adc_value = self.extract_number(data,12,13)
        print ( f"power meassured: {optical_power}  mode {mode} freq {wavelength} pwr_gear {batteryLevel}")
        return (optical_power , mode, wavelength , batteryLevel)

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

    def read_the_value_of_corresponding_address_of_eeprom(self, address):
        # This command needs the specific address to read from, so it's a special case
        base_command = b'\xAA\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # Placeholder command
        # Here you'd modify the command to include the specific address. This is just a placeholder example.
        # actual_command = modify_command_with_address(base_command, address)
        # return send_data(actual_command)
        pass  # Implement the address modification logic

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

