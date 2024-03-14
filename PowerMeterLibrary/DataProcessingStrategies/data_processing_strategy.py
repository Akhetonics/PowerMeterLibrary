from device_controller import DeviceController


class DataProcessingStrategy:
    def __init__(self, function_nr, function_sub_id):
        self.function_nr = function_nr
        self.function_sub_id = function_sub_id

    def process_data(self, controller , data):
        raise NotImplementedError

    def applies_to(self, function_nr, function_sub_id):
        return self.function_nr == function_nr and self.function_sub_id == function_sub_id
    
