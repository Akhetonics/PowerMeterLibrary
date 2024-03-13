from enum import Enum, unique

@unique
class Commands(Enum):
    RETURN_POWER_ADC_FREQUENCY                          = b'\xAA\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    RETURN_POWER_WAVELENGTH_BATTERY                     = b'\xAA\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    RETURN_POWER_REFERENCE_POWER                        = b'\xAA\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    SWITCH_WAVELENGTH_GEAR_AND_READ_REFERENCE_POWER     = b'\xAA\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    SWITCH_WAVELENGTH_GEAR_DIRECTLY                     = b'\xAA\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    SWITCH_OPTICAL_POWER_UNIT_TO_UW                     = b'\xAA\x02\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    SWITCH_OPTICAL_POWER_UNIT_TO_DBM                    = b'\xAA\x02\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    SWITCH_TO_VIEW_REFERENCE_VALUE_MODE                 = b'\xAA\x02\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    SET_CURRENT_OPTICAL_POWER_AS_REFERENCE              = b'\xAA\x02\x03\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    SWITCH_LED_BACKLIGHT_OFF                            = b'\xAA\x02\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    TURN_ON_LED_BACKLIGHT                               = b'\xAA\x02\x04\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00'
    TURN_OFF_LED_BACKLIGHT                              = b'\xAA\x02\x04\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    AUTO_POWER_OFF                                      = b'\xAA\x03\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    AUTOMATIC_SHUTDOWN_ON                               = b'\xAA\x03\x07\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    RESET_OPTICAL_POWER_REFERENCE_VALUE                 = b'\xAA\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    DELETE_ALL_RECORDS_OF_EEPROM                        = b'\xAA\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    READ_THE_VALUE_OF_CORRESPONDING_ADDRESS_OF_EEPROM   = b'\xAA\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # Placeholder, needs the specific address to read from
    RETURNS_THE_NUMBER_OF_STORED_POWER_RECORDS          = b'\xAA\x22\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    CLEAR_STORED_POWER_RECORDS                          = b'\xAA\x19\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

@unique 
class CommandTypes (Enum):
    POWER_REQUEST = 0x01  # a request of type "please send me the power" is being sent.
    DISPLAY_SETTINGS_CHANGE = 0x02  # a request is being sent to please change the device's internal display settings