# Optical Power Meter FOPM-203/204 Communication and Data Processing Framework

This repository contains a Python-based framework designed to facilitate communication with a specific device (e.g., a power meter) and process the data it provides. It employs a strategy pattern to dynamically load and apply data processing algorithms based on the received data, ensuring extensibility and modularity.

<img src="https://github.com/Akhetonics/PowerMeterLibrary/assets/18228325/66fdfefe-dc74-4bbf-9409-1947b7095994" width="100">

https://resource.fs.com/mall/doc/20230602112425818oyi.pdf

## Features

- Dynamic loading of data processing strategies.
- `async` data receiving in backgroundthread
- Communication with devices via serial port.
- Auto-connect with device finding mechanism
- Processing of optical power, wavelength, and battery level data.
- Console commands are prepared to control the device using console if wanted
- Extensible architecture to add more data processing strategies.

## Supported Commands
- RETURN_POWER_ADC_FREQUENCY
- RETURN_POWER_WAVELENGTH_BATTERY
- RETURN_POWER_REFERENCE_POWER
- SWITCH_WAVELENGTH_GEAR_AND_READ_REFERENCE_POWER 
- SWITCH_WAVELENGTH_GEAR_DIRECTLY
- SWITCH_OPTICAL_POWER_UNIT_TO_UW 
- SWITCH_OPTICAL_POWER_UNIT_TO_DBM
- SWITCH_TO_VIEW_REFERENCE_VALUE_MODE
- SET_CURRENT_OPTICAL_POWER_AS_REFERENCE
- SWITCH_LED_BACKLIGHT
- TURN_ON_LED_BACKLIGHT
- TURN_OFF_LED_BACKLIGHT
- AUTO_POWER_OFF
- AUTOMATIC_SHUTDOWN_ON
- RESET_OPTICAL_POWER_REFERENCE_VALUE
- DELETE_ALL_RECORDS_OF_EEPROM
- READ_THE_VALUE_OF_CORRESPONDING_ADDRESS_OF_EEPROM (not fully implemented)
- RETURNS_THE_NUMBER_OF_STORED_POWER_RECORDS (not fully implemented)
- CLEAR_STORED_POWER_RECORDS

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your system.
- `pyserial==3.5` library installed.

## Installation

Clone the repository to your local machine using:

```bash
git clone git@github.com:Akhetonics/PowerMeterLibrary.git
```

## Troubleshooting

- *Device Not Found:* Ensure your device is properly connected - the cable often falls out - and the correct port (usually com3) is available. Try reconnecting your device or restarting the script. (often you might have multiple instances of the script running which will block the serial port.)
- *Data Processing Issues:* Verify that your data processing strategies are correctly implemented and can handle the data formats sent by your device. -> not all commands'es responses are implemented, but most are. just add a class into the DataProcessing folder and strucutre it similar like the others. make sure the identifying two numbers are defined properly.

## Usage

To start using this framework, perform the following steps:

1. Ensure your device is connected to the computer.
2. Run the main script to start the communication and data processing:

```bash
python OpticalPowerMeter.py
```

