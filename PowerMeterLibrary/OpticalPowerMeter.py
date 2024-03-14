import asyncio
from commands import Commands
from console_helper import async_input, handle_console
from device_controller import DeviceController

# create a controller and connect to the device
async def main():
    async with DeviceController(connectionTimeout=60) as controller:
        # start powermeter controller in background thread
        controller.start_update_in_background()
        print("welcome. print 'help' for a quick command reference")

        while True:
            # handles the console input like 'help' or 'start' and 'stop'
            await handle_console(controller, input)
            await asyncio.sleep(0.01)

# another example where we directly access and print the controller variables
async def main2():
    async with DeviceController(connectionTimeout=60) as controller:
        while True:
            # ask the power meter to send us the power
            controller.send_command(Commands.RETURN_POWER_WAVELENGTH_BATTERY)
            # wait until the response is there
            await controller.wait_for_power_data_change_async()
            print(f"power: {controller.optical_power} μW\t λ: {controller.wavelength} nm\t🔋 {controller.battery_level} \t")

if __name__ == "__main__":
    asyncio.run(main2())

