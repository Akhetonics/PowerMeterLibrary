# Optical Power Meter Communication and Data Processing Framework

This repository contains a Python-based framework designed to facilitate communication with a specific device (e.g., a power meter) and process the data it provides. It employs a strategy pattern to dynamically load and apply data processing algorithms based on the received data, ensuring extensibility and modularity.

## Features

- Dynamic loading of data processing strategies.
- Communication with devices via serial port.
- Processing of optical power, wavelength, and battery level data.
- Extensible architecture to add more data processing strategies.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your system.
- `pyserial==3.5` library installed.

## Installation

Clone the repository to your local machine using:

```bash
git clone <repository-url>
```
## Troubleshooting

- *Device Not Found:* Ensure your device is properly connected - the cable often falls out - and the correct port (usually com3) is available. Try reconnecting your device or restarting the script. (often you might have multiple instances of the script running which will block the serial port.)
- *Data Processing Issues:* Verify that your data processing strategies are correctly implemented and can handle the data formats sent by your device. -> not all commands'es responses are implemented, but most are. just add a class into the DataProcessing folder and strucutre it similar like the others. make sure the identifying two numbers are defined properly.

## Usage

To start using this framework, perform the following steps:

1. Ensure your device is connected to the computer.
2. Run the main script to start the communication and data processing:

```bash
python main_script.py
```

Replace `main_script.py` with the actual entry script of your project if it's named differently.

