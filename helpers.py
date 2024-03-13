
import struct


def convert_number_to_wavelength(index):
    wavelengths = {
        0: 850,
        1: 1300,
        2: 1310,
        3: 1490,
        4: 1550,
        5: 1625
    }
    return wavelengths.get(index, None)

def extract_number(data, start, end):
        # Determine the number of bytes
        num_bytes = end - start
        
        # Choose the appropriate format specifier based on the number of bytes
        format_specifier = {1: 'B', 2: 'H', 4: 'f'}.get(num_bytes)
        if format_specifier is None:
            raise ValueError("Unsupported number of bytes")
        
        # Unpack the data using the chosen format specifier
        extracted_value = struct.unpack('<' + format_specifier, data[start:end])[0]
        return extracted_value