from __future__ import division

from time import sleep, time
from threading import Event
from collections import deque

from RPi import GPIO
from w1thermsensor import W1ThermSensor

from .devices import GPIODeviceError, GPIODevice, GPIOThread


class InputDeviceError(GPIODeviceError):
    pass


class InputDevice(GPIODevice):
    def __init__(self, pin=None, pull_up=True):
        super(InputDevice, self).__init__(pin)
        self._pull_up = pull_up
        self._edge = (GPIO.RISING, GPIO.FALLING)[pull_up]
        if pull_up:
            self._active_state = 0
            self._inactive_state = 1
        GPIO.setup(pin, GPIO.IN, (GPIO.PUD_DOWN, GPIO.PUD_UP)[pull_up])

    @property
    def pull_up(self):
        return self._pull_up


class Button(InputDevice):
    pass


class MotionSensor(InputDevice):
    def __init__(
            self, pin=None, queue_len=5, sample_rate=10, threshold=0.5,
            partial=False):
        super(MotionSensor, self).__init__(pin, pull_up=False)
        if queue_len < 1:
            raise InputDeviceError('queue_len must be at least one')
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.partial = partial
        self._queue = deque(maxlen=queue_len)
        self._queue_full = Event()
        self._queue_thread = GPIOThread(target=self._fill_queue)
        self._queue_thread.start()

    @property
    def queue_len(self):
        return self._queue.maxlen

    @property
    def value(self):
        if not self.partial:
            self._queue_full.wait()
        try:
            return sum(self._queue) / len(self._queue)
        except ZeroDivisionError:
            # No data == no motion
            return 0.0

    @property
    def motion_detected(self):
        return self.value > self.threshold

    def _get_sample_rate(self):
        return self._sample_rate
    def _set_sample_rate(self, value):
        if value <= 0:
            raise InputDeviceError('sample_rate must be greater than zero')
        self._sample_rate = value
    sample_rate = property(_get_sample_rate, _set_sample_rate)

    def _get_threshold(self):
        return self._threshold
    def _set_threshold(self, value):
        if value < 0:
            raise InputDeviceError('threshold must be zero or more')
        self._threshold = value
    threshold = property(_get_threshold, _set_threshold)

    def _fill_queue(self):
        while (
                not self._queue_thread.stopping.wait(1 / self.sample_rate) and
                len(self._queue) < self._queue.maxlen
            ):
            self._queue.append(self.is_active)
        self._queue_full.set()
        while not self._queue_thread.stopping.wait(1 / self.sample_rate):
            self._queue.append(self.is_active)


class LightSensor(InputDevice):
    def __init__(
            self, pin=None, queue_len=5, darkness_time=0.01,
            threshold=0.1, partial=False):
        super(LightSensor, self).__init__(pin, pull_up=False)
        if queue_len < 1:
            raise InputDeviceError('queue_len must be at least one')
        self.darkness_time = darkness_time
        self.threshold = threshold
        self.partial = partial
        self._charged = Event()
        GPIO.add_event_detect(self.pin, GPIO.RISING, lambda channel: self._charged.set())
        self._queue = deque(maxlen=queue_len)
        self._queue_full = Event()
        self._queue_thread = GPIOThread(target=self._fill_queue)
        self._last_state = None
        self._when_light = None
        self._when_dark = None
        self._when_light_event = Event()
        self._when_dark_event = Event()
        self._queue_thread.start()

    @property
    def queue_len(self):
        return self._queue.maxlen

    @property
    def value(self):
        if not self.partial:
            self._queue_full.wait()
        try:
            return 1.0 - (sum(self._queue) / len(self._queue)) / self.darkness_time
        except ZeroDivisionError:
            # No data == no light
            return 0.0

    @property
    def light_detected(self):
        return self.value > self.threshold

    def _get_when_light(self):
        return self._when_light
    def _set_when_light(self, value):
        if not callable(value) and value is not None:
            raise InputDeviceError('when_light must be None or a function')
        self._when_light = value
    when_light = property(_get_when_light, _set_when_light)

    def _get_when_dark(self):
        return self._when_dark
    def _set_when_dark(self, value):
        if not callable(value) and value is not None:
            raise InputDeviceError('when_dark must be None or a function')
        self._when_dark = value

    def wait_for_light(self, timeout=None):
        self._when_light_event.wait(timeout)

    def wait_for_dark(self, timeout=None):
        self._when_dark_event.wait(timeout)

    def _get_darkness_time(self):
        return self._darkness_time
    def _set_darkness_time(self, value):
        if value <= 0.0:
            raise InputDeviceError('darkness_time must be greater than zero')
        self._darkness_time = value
        # XXX Empty the queue and restart the thread
    darkness_time = property(_get_darkness_time, _set_darkness_time)

    def _get_threshold(self):
        return self._threshold
    def _set_threshold(self, value):
        if value < 0:
            raise InputDeviceError('threshold must be zero or more')
        self._threshold = value
    threshold = property(_get_threshold, _set_threshold)

    def _fill_queue(self):
        try:
            while (
                    not self._queue_thread.stopping.is_set() and
                    len(self._queue) < self._queue.maxlen
                ):
                self._queue.append(self._time_charging())
                if self.partial:
                    self._fire_events()
            self._queue_full.set()
            while not self._queue_thread.stopping.is_set():
                self._queue.append(self._time_charging())
                self._fire_events()
        finally:
            GPIO.remove_event_detect(self.pin)

    def _time_charging(self):
        # Drain charge from the capacitor
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        sleep(0.1)
        # Time the charging of the capacitor
        start = time()
        self._charged.clear()
        GPIO.setup(self.pin, GPIO.IN)
        self._charged.wait(self.darkness_time)
        return min(self.darkness_time, time() - start)

    def _fire_events(self):
        last_state = self._last_state
        self._last_state = state = self.light_detected
        if not last_state and state:
            self._when_dark_event.clear()
            self._when_light_event.set()
            if self.when_light:
                self.when_light()
        elif last_state and not state:
            self._when_light_event.clear()
            self._when_dark_event.set()
            if self.when_dark:
                self.when_dark()

class TemperatureSensor(W1ThermSensor):
    @property
    def value(self):
        return self.get_temperature()


