from machine import Pin
from lib.ulogging import uLogger
from asyncio import Event, sleep

class Button:

    def __init__(self, GPIO_pin: int, button_name: str, button_pressed_event: Event) -> None:
        self.logger = uLogger(f"Button {GPIO_pin}")
        self.gpio = GPIO_pin
        self.pin = Pin(GPIO_pin, Pin.IN, Pin.PULL_UP)
        self.name = button_name
        self.button_pressed = button_pressed_event
   
    async def wait_for_press(self) -> None:
        self.logger.info(f"Starting button press watcher for button: {self.name}")

        while True:
            current_value = self.pin.value()
            active = 0
            while active < 20:
                if self.pin.value() != current_value:
                    active += 1
                else:
                    active = 0
                await sleep(0.001)

            if self.pin.value() == 0:
                self.logger.info(f"Button pressed: {self.name}")
                self.button_pressed.set()
            else:
                self.logger.info(f"Button released: {self.name}")

    def get_name(self) -> str:
        return self.name
    
    def get_pin(self) -> int:
        return self.gpio
