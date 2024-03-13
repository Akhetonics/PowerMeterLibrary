import time
from device_controller import DeviceController, DataValidationError, DataLengthError, StartByteError, FunctionNumberError, FunctionSubNumberError

# connect to the device
controller = DeviceController()
controller.connect_to_device()

try:
    while True:
        try:
            power = controller.get_current_optical_power()
            # Use the power variable as needed
            pass
        except DataValidationError as e:
            print(e)
        time.sleep(0.1)
finally:
    # This block ensures the serial port is closed even if the script is interrupted
    controller.close_serial_port()
    print("Serial port closed.")