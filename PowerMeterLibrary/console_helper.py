import asyncio
import sys

from commands import Commands

async def async_input(prompt: str = "") -> str:
    return await asyncio.to_thread(input, prompt)


async def handle_console(controller, input):
    
    input = await async_input()
    if(input == "data"):
        print(f"{(controller.device_response_time):.2f} ms > power: {controller.optical_power} μW \t λ: {controller.wavelength} nm\t🔋 {controller.battery_level} \tADC: {controller.adc_value} \t ref_pwr: {controller.reference_power} ")
    elif (input == "help"):
        print(f"you can enter the following commands: \n'data', 'battery', 'start', 'stop', 'light', 'exit', ")
    elif(input =="battery"):
        print(f"🔋 {controller.battery_level} ")
    elif (input == "start"):
        print("start printing data. enter 'stop' to abort.")
        await asyncio.sleep(0.2)
        controller.do_print_data = True
    elif (input == "stop"):
        controller.do_print_data = False
    elif (input == "light"):
        controller.send_command(Commands.SWITCH_LED_BACKLIGHT)
        if await controller.wait_for_display_settings_change(1) == True:
            print("light has changed")
        else:
            print("error")
    elif (input == "exit"):
        sys.exit()
    else:
        print( "incorrect command: " + input)
