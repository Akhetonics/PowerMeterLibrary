
from DataProcessingStrategies.data_processing_strategy import DataProcessingStrategy
from device_controller import DeviceController
from helpers import extract_number


class OpticalPowerAndADC(DataProcessingStrategy):
    def __init__(self):
        super().__init__(function_nr=1, function_sub_id=0)

    def process_data(self, controller :DeviceController, data):
        controller.optical_power = extract_number(data,5,9)
        controller.adc_value = extract_number(data,9,11)
        controller.frequency = extract_number(data,11,12)
        controller.power_adjustment_gear = extract_number(data,12,13)