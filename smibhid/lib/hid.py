from ulogging import uLogger
from asyncio import get_event_loop
from space_state import SpaceState
from error_handling import ErrorHandler
from module_config import ModuleConfig
from display import Display
from networking import WirelessNetwork

class HID:
    
    def __init__(self) -> None:
        """
        Human Interface Device for event spaces providing buttons and status LEDs for space open state.
        Create HID instance and then run startup() to start services for button monitoring and LED output.
        """
        self.log = uLogger("HID")
        self.version = "1.1.1"
        self.loop_running = False
        self.moduleConfig = ModuleConfig(Display(), WirelessNetwork())
        self.moduleConfig.enable_network_status_monitor()
        self.display = self.moduleConfig.get_display()
        self.spaceState = SpaceState(self.moduleConfig)
        self.errorHandler = ErrorHandler("HID")
        self.errorHandler.configure_display(self.display)
        
    def startup(self) -> None:
        """
        Initialise all aysnc services for the HID.
        """
        self.log.info("--------Starting SMIBHID--------")
        self.log.info(f"SMIBHID firmware version: {self.version}")
        self.display.clear()
        self.display.print_startup(self.version)
        self.spaceState.startup()
      
        self.log.info("Entering main loop")        
        self.loop_running = True
        loop = get_event_loop()
        loop.run_forever()