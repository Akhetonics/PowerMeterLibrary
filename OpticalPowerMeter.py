import time
from DataProcessingStrategies.optical_power_and_wavelength import OpticalPowerAndWavelength
from DataProcessingStrategies.optical_power_and_adc import OpticalPowerAndADC
from commands import Commands
from device_controller import DeviceController, DataValidationError

# connect to the device
strategies = [OpticalPowerAndADC(), OpticalPowerAndWavelength()]

with DeviceController(strategies) as controller:
    controller.send_command(Commands.TURN_ON_LED_BACKLIGHT )
    while True:
        try:
            #controller.send_command(Commands.RETURN_CURRENT_OPTICAL_POWER.value)
            controller.send_command(Commands.RETURN_POWER_WAVELENGTH_BATTERY )
        except DataValidationError as e:
            print(e)
        controller.receive_data()
        print(f"power measured: {controller.optical_power}  adc {controller.adc_value} freq {controller.frequency} pwr_gear {controller.power_adjustment_gear} battery {controller.battery_level}")
        time.sleep(0.1)
