import asyncio
from console_helper import handle_console
from device_controller import DeviceController

# create a controller and connect to the device
async def main():
    async with DeviceController(connectionTimeout=60) as controller:
        controller.start_update_in_background()
        print("welcome. print 'help' for a quick command reference")

        while True:    
            await handle_console(controller, input)
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(main())



