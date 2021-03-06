from RPi import GPIO

from .devices import GPIODeviceError, GPIODevice, GPIOThread


class OutputDeviceError(GPIODeviceError):
    pass


class OutputDevice(GPIODevice):
    def __init__(self, pin=None):
        super(OutputDevice, self).__init__(pin)
        GPIO.setup(pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, True)

    def off(self):
        GPIO.output(self.pin, False)


class LED(OutputDevice):
    def __init__(self, pin=None):
        super(LED, self).__init__(pin)
        self._blink_thread = None

    def blink(self, on_time, off_time):
        self._stop_blink()
        self._blink_thread = GPIOThread(target=self._blink_led, args=(on_time, off_time))
        self._blink_thread.start()

    def _stop_blink(self):
        if self._blink_thread:
            self._blink_thread.stop()
            self._blink_thread = None

    def _blink_led(self, on_time, off_time):
        while True:
            super(LED, self).on()
            if self._blink_thread.stopping.wait(on_time):
                break
            super(LED, self).off()
            if self._blink_thread.stopping.wait(off_time):
                break

    def on(self):
        self._stop_blink()
        super(LED, self).on()

    def off(self):
        self._stop_blink()
        super(LED, self).off()


class Buzzer(OutputDevice):
    pass


class Motor(OutputDevice):
    pass
