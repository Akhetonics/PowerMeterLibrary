from DataProcessingStrategies.data_processing_strategy import DataProcessingStrategy
from device_controller import DeviceController
from helpers import extract_number


class OpticalPowerAndReferencePower(DataProcessingStrategy):
    def __init__(self):
        super().__init__(function_nr=1, function_sub_id=1)

    def process_data(self, controller , data):
        controller.optical_power = extract_number(data,5,9)
        controller.reference_power = extract_number(data,9,13)