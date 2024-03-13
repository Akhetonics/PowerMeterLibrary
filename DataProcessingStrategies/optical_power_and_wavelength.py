
from DataProcessingStrategies.data_processing_strategy import DataProcessingStrategy
from device_controller import DeviceController
from helpers import convert_number_to_wavelength, extract_number


class OpticalPowerAndWavelength(DataProcessingStrategy):
    def __init__(self):
        super().__init__(function_nr=1, function_sub_id=0x80)
        
    def process_data(self , controller, data) -> None:
        controller.optical_power = extract_number(data,5,9)
        controller.mode = extract_number(data,9,10)
        controller.wavelength = convert_number_to_wavelength(extract_number(data,10,11))
        controller.battery_level = (extract_number(data,11,12)+1) * 25 # the battery has the number 0,1,2,3 where 3 is 100% and 0 is empty (because it has 3 bars in the device screen)