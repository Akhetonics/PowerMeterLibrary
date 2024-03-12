import serial
import time
import struct 
import serial.tools.list_ports


def send_data(data):
    ser.write(data)  # Send data
    time.sleep(0.1)  # Short pause to ensure all data is transmitted

def receive_data():
    data = ser.read(14)  # Receive 13 bytes of data
    return data

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

class Strategy:
    def handle(self, data, function_nr, function_sub_id):
        pass

class ReadCurrentPowerStrategy(Strategy):
    def handle(self, data, function_nr, function_sub_id):
        optical_power = Parser.extract_number(data,5,9)
        adc_value = Parser.extract_number(data,9,11)
        frequency = adc_value = Parser.extract_number(data,11,12)
        power_adjustment_gear = adc_value = Parser.extract_number(data,12,13)
        print ( f"power meassured: {optical_power}  adc {adc_value} freq {frequency} pwr_gear {power_adjustment_gear}")

class ReadCurrentPowerReferenceStrategy(Strategy):
    def handle(self, data, function_nr, function_sub_id):
        optical_power = Parser.extract_number(data,5,9)
        mode = Parser.extract_number(data,9,10)
        wavelength = adc_value = Parser.extract_number(data,11,12)
        batteryLevel = adc_value = Parser.extract_number(data,12,13)
        print ( f"power meassured: {optical_power}  mode {mode} freq {wavelength} pwr_gear {batteryLevel}")


# Add more strategy classes as needed for different function numbers

class Parser:
    def __init__(self):
        self.strategies = {}

    def add_strategy(self, function_nr, function_sub_id, strategy):
        self.strategies[(function_nr,function_sub_id)] = strategy

    @staticmethod
    def extract_number(data, start, end):
        # Determine the number of bytes
        num_bytes = end - start
        
        # Choose the appropriate format specifier based on the number of bytes
        format_specifier = {1: 'B', 2: 'H', 4: 'I'}.get(num_bytes)
        if format_specifier is None:
            raise ValueError("Unsupported number of bytes")
        
        # Unpack the data using the chosen format specifier
        extracted_value = struct.unpack('>' + format_specifier, data[start:end])[0]
        return extracted_value
    
    def parse_data(self, data):
        if data is not None and len(data) == 13:
            start_byte = hex(self.extract_number(data,0,1))
            function_nr = self.extract_number(data,1,2)
            function_sub_id = self.extract_number(data,2,3)
            
            
            if (function_nr, function_sub_id) in self.strategies:  # Check both function_nr and function_sub_id
                strategy = self.strategies[(function_nr, function_sub_id)]
                strategy.handle(data, function_nr, function_sub_id)
            else:
                print(f"No strategy found for function nr {function_nr} and sub id {function_sub_id}")
        else:
            print("Fehler: Nicht genug Daten erhalten.")
        
parser = Parser()
parser.add_strategy(1,  0 , ReadCurrentPowerStrategy())
parser.add_strategy(1, 0x80 , ReadCurrentPowerReferenceStrategy())

def check_serial_ports():
    available_ports = serial.tools.list_ports.comports()
    for port in available_ports:
        print(f"Trying port: {port.device}")
        try:
            ser = serial.Serial(port.device, 9600, timeout=1)
            ser.write(commands["return_current_optical_power"])  # Send command
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

# Call the function to check available serial ports
selected_port = check_serial_ports()

# Configuration of the serial interface
ser = serial.Serial(selected_port, 9600, timeout=1)  # Check the correct COM port and baud rate

while True:
        
    # Example of sending a command to get current optical power
    send_data(commands["return_current_optical_power_reference"])

    # Example of receiving data
    received_data = receive_data()
    parser.parse_data(received_data)
    time.sleep(0.1)
# Important: Make sure to properly open and close the serial port when finished.
ser.close()