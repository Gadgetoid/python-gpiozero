from .input_devices import Button
from .output_devices import LED
from .devices import GPIODeviceError


class TrafficLights(object):
    def __init__(self, red=None, amber=None, green=None):
        if not all([red, amber, green]):
            raise GPIODeviceError('Red, Amber and Green pins must be provided')

        self.red = LED(red)
        self.amber = LED(amber)
        self.green = LED(green)
        self.lights = [self.red, self.amber, self.green]

    def lights_on(self):
        for led in self.lights:
            led.on()

    def lights_off(self):
        for led in self.lights:
            led.off()


class PiTraffic(TrafficLights):
    def __init__(self):
        self.red = LED(9)
        self.amber = LED(10)
        self.green = LED(11)
        self.lights = [self.red, self.amber, self.green]


class FishDish(TrafficLights):
    def __init__(self):
        red, amber, green = (9, 22, 4)
        super(FishDish, self).__init__(red, amber, green)
        self.buzzer = Buzzer(8)
        self.button = Button(7)
        self.all = self.lights + [self.buzzer]

    def on(self):
        for led in self.all:
            led.on()

    def off(self):
        for led in self.all:
            led.off()


class PiLiter(object):
    def __init__(self):
        leds = [4, 17, 27, 18, 22, 23, 24, 25]
        self.leds = [LED(led) for led in leds]

    def on(self):
        for led in self.leds:
            led.on()

    def off(self):
        for led in self.leds:
            led.off()
