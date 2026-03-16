import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_ssd1306

kbd = Keyboard(usb_hid.devices)

button_pins = [
    board.D0, board.D1, board.D2,
    board.D3, board.D4, board.D5,
    board.D6, board.D7, board.D8
]

buttons = []

for pin in button_pins:
    b = digitalio.DigitalInOut(pin)
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP
    buttons.append(b)

displayio.release_displays()

i2c = board.I2C()

display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_ssd1306.SSD1306(display_bus, width=128, height=64)

splash = displayio.Group()

text = label.Label(
    terminalio.FONT,
    text="Zuup Macropad Ready",
    x=10,
    y=30
)

splash.append(text)
display.root_group = splash

def run_macro(num):

    text.text = "Key " + str(num+1)

    if num == 0:
        kbd.send(Keycode.CONTROL, Keycode.C)

    elif num == 1:
        kbd.send(Keycode.CONTROL, Keycode.V)

    elif num == 2:
        kbd.send(Keycode.CONTROL, Keycode.Z)

    elif num == 3:
        kbd.send(Keycode.CONTROL, Keycode.S)

    elif num == 4:
        kbd.send(Keycode.ALT, Keycode.TAB)

    elif num == 5:
        kbd.send(Keycode.WINDOWS, Keycode.D)

    elif num == 6:
        kbd.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.ESC)

    elif num == 7:
        kbd.send(Keycode.CONTROL, Keycode.A)

    elif num == 8:
        kbd.send(Keycode.ENTER)

while True:

    for i, button in enumerate(buttons):

        if not button.value:
            run_macro(i)

            while not button.value:
                pass

            time.sleep(0.1)