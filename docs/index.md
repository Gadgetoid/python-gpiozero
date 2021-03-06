# gpio-zero

A simple interface to everyday GPIO components used with Raspberry Pi

## Why?

The "hello world" program in Java is at least 5 lines long, and contains 11
jargon words which are to be ignored. The "hello world" program in Python is
one simple line. However, the "hello world" of physical computing in Python
(flashing an LED) is similar to the Java program:

```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

red = 2

GPIO.setup(red, GPIO.OUT)

GPIO.output(red, True)
```

6 lines of code to flash an LED. And skipping over why `GPIO` is used twice in
the first line; what `BCM` means; why set warnings to False; and so on. Young
children and beginners shouldn't need to sit and copy out several lines of text
they're told to ignore. They should be able to read their code and understand
what it means. This module provides a simple interface to everyday components.
The LED example becomes:

```python
from gpiozero import LED

red = LED(2)

red.on()
```

Any guesses how to turn it off?

## Implemented Components

- LED
- Buzzer
- Button
- Motion Sensor
- Light Sensor
- Temperature Sensor
- Motor

## Usage

### LED

Turn an LED on and off repeatedly:

```python
from gpiozero import LED
from time import sleep

red = LED(2)

while True:
    red.on()
    sleep(1)
    red.off()
    sleep(1)
```

Alternatively:

```python
from gpiozero import LED
from time import sleep

red = LED(2)
red.blink(1, 1)
sleep(10)
```

### Buzzer

Turn a buzzer on and off repeatedly:

```python
from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(3)

while True:
    buzzer.on()
    sleep(1)
    buzzer.off()
    sleep(1)
```

### Button

Check if a button is pressed:

```python
from gpiozero import Button

button = Button(4)

if button.is_active:
    print("Button is pressed")
else:
    print("Button is not pressed")
```

Wait for a button to be pressed before continuing:

```python
from gpiozero import Button

button = Button(4)

button.wait_for_input()
print("Button was pressed")
```

Run a function every time the button is pressed:

```python
from gpiozero import Button

def hello(pin):
    print("Button was pressed")

button = Button(4)

button.add_callback(hello)
```

### Motion Sensor

Detect motion:

```python
from gpiozero import MotionSensor

pir = MotionSensor(5)

while True:
    if pir.motion_detected:
        print("Motion detected")
```

### Light Sensor

Retrieve light sensor value:

```python
from time import sleep
from gpiozero import LightSensor

sensor = LightSensor(18)
led = LED(16)

sensor.when_dark = led.on
sensor.when_light = led.off

while True:
    sleep(1)
```

### Temperature Sensor

Retrieve light sensor value:

```python
from gpiozero import TemperatureSensor

temperature = TemperatureSensor(6)

print(temperature.value)
```

### Motor

Drive two motors forwards for 5 seconds:

```python
from gpiozero import Motor
from time import sleep

left_motor = Motor(7)
right_motor = Motor(8)

left_motor.on()
right_motor.on()
sleep(5)
left_motor.off()
right_motor.off()
```
