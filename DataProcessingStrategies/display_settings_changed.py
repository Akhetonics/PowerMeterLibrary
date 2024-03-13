
from DataProcessingStrategies.data_processing_strategy import DataProcessingStrategy
from device_controller import DeviceController
from helpers import convert_number_to_wavelength, extract_number

# could be light off or light on or switching the unit or setting the reference power value
class DisplaySettingsChanged(DataProcessingStrategy):
    def __init__(self):
        super().__init__(function_nr=0x02, function_sub_id=0)
        
    def process_data(self , controller : DeviceController, data) -> None:
        controller.display_settings_changed = True
        return