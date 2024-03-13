import time
from DataProcessingStrategies.data_processing_strategy import DataProcessingStrategy
from StrategyLoader import DataProcessingStrategyLoader
from commands import Commands
from device_controller import DeviceController, DataValidationError

# create a controller and connect to the device
loader = DataProcessingStrategyLoader("DataProcessingStrategies" , DataProcessingStrategy.__name__) # load all response processing strategies from folder

with DeviceController(loader.strategies, connectionTimeout=60) as controller:
    controller.send_command(Commands.TURN_ON_LED_BACKLIGHT)
    if controller.wait_for_display_settings_change(0.25) == False: # send again if timeout occured
            controller.send_command(Commands.TURN_OFF_LED_BACKLIGHT)
    while True:
        try:
            start_time = time.perf_counter()
            controller.send_command(Commands.RETURN_POWER_WAVELENGTH_BATTERY)
            controller.wait_for_power_data_change(2)
            end_time = time.perf_counter()
            print(f"{((end_time - start_time) *1000):.2f} ms > power measured: {controller.optical_power} \twaveLength {controller.wavelength} \tbattery {controller.battery_level}")
            time.sleep(0.1)
        except DataValidationError as e:
            print(e)



