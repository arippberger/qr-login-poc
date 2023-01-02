import badger2040
import qrcode
import time
import os
import badger_os
import base64
import hashlib
import binascii
from totp import totp
from machine import Pin

secret = 'secret'
pin_string = ''
one_time_password = ()
rtc = machine.RTC()
time_remaining = 0
changed = False

def a_button_callback(pin):
    global pin_string
    changed = False
    pin_string += 'a'
    print(pin_string)
    
def b_button_callback(pin):
    global pin_string
    changed = False
    pin_string += 'b'
    print(pin_string)
    
def c_button_callback(pin):
    global pin_string
    changed = False
    pin_string += 'c'
    print(pin_string)
    
button_a = Pin(badger2040.BUTTON_A,Pin.IN,Pin.PULL_DOWN)
button_a.irq(trigger=Pin.IRQ_FALLING, handler=a_button_callback)
button_b = Pin(badger2040.BUTTON_B,Pin.IN,Pin.PULL_DOWN)
button_b.irq(trigger=Pin.IRQ_FALLING, handler=b_button_callback)
button_c = Pin(badger2040.BUTTON_C,Pin.IN,Pin.PULL_DOWN)
button_c.irq(trigger=Pin.IRQ_FALLING, handler=c_button_callback)

display = badger2040.Badger2040()

def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.pen(15)
    display.rectangle(ox, oy, size, size)
    display.pen(0)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)
                
def draw_button_text():
    display.pen(15)
    display.thickness(1)
    display.rectangle(
        127, # int: x coordinate of the rectangle's top left corner
        0, # int: y coordinate of the rectangle's top left corner
        170, # int: width of rectangle
        128  # int: height of rectangle
    )
    display.pen(0)
    display.text(
        'Provide PIN and press ENTER', # string: the text to draw
        128,            # int: x coordinate for the left middle of the text
        5,            # int: y coordinate for the left middle of the text
        scale=0.38,    # float: size of the text
        rotation=0.0  # float: rotation of the text in degrees
    )
    display.thickness(2)
    display.text(
        'RESET', # string: the text to draw
        250,            # int: x coordinate for the left middle of the text
        30,            # int: y coordinate for the left middle of the text
        scale=0.5,    # float: size of the text
        rotation=0.0  # float: rotation of the text in degrees
    )
    display.text(
        'ENTER', # string: the text to draw
        250,            # int: x coordinate for the left middle of the text
        95,            # int: y coordinate for the left middle of the text
        scale=0.5,    # float: size of the text
        rotation=0.0  # float: rotation of the text in degrees
    )
    
def draw_intro_text():
    display.pen(15)
    display.thickness(2)
    display.rectangle(
        0, # int: x coordinate of the rectangle's top left corner
        0, # int: y coordinate of the rectangle's top left corner
        296, # int: width of rectangle
        128  # int: height of rectangle
    )
    display.pen(0)
    display.text(
        'Provide PIN and press ENTER', # string: the text to draw
        1,            # int: x coordinate for the left middle of the text
        5,            # int: y coordinate for the left middle of the text
        scale=0.5,    # float: size of the text
        rotation=0.0  # float: rotation of the text in degrees
    )
    display.text(
        'RESET', # string: the text to draw
        250,            # int: x coordinate for the left middle of the text
        30,            # int: y coordinate for the left middle of the text
        scale=0.5,    # float: size of the text
        rotation=0.0  # float: rotation of the text in degrees
    )
    display.text(
        'ENTER', # string: the text to draw
        250,            # int: x coordinate for the left middle of the text
        95,            # int: y coordinate for the left middle of the text
        scale=0.5,    # float: size of the text
        rotation=0.0  # float: rotation of the text in degrees
    )
    display.text(
        'A', # string: the text to draw
        40,            # int: x coordinate for the left middle of the text
        120,            # int: y coordinate for the left middle of the text
        scale=0.5,    # float: size of the text
        rotation=0.0  # float: rotation of the text in degrees
    )
    display.text(
        'B', # string: the text to draw
        145,            # int: x coordinate for the left middle of the text
        120,            # int: y coordinate for the left middle of the text
        scale=0.5,    # float: size of the text
        rotation=0.0  # float: rotation of the text in degrees
    )
    display.text(
        'C', # string: the text to draw
        250,            # int: x coordinate for the left middle of the text
        120,            # int: y coordinate for the left middle of the text
        scale=0.5,    # float: size of the text
        rotation=0.0  # float: rotation of the text in degrees
    )


# wake = not badger2040.woken_by_button()
draw_intro_text()
display.update()
year, month, day, wd, hour, minute, second, _ = rtc.datetime()
last_second = second

while True:
    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
        
    if display.pressed(badger2040.BUTTON_UP): 
        pin_string = ''
        display.update_speed(badger2040.UPDATE_NORMAL)
        display.clear()
        draw_intro_text()
        display.update()
        time.sleep_ms(250)
        
    if display.pressed(badger2040.BUTTON_DOWN):
        print(str(month) + '/' + str(day) + '/' + str(year) + ' ' + str(hour) + ':' + str(minute) + ':' + str(second))
        changed = True
        
    if second != last_second and time_remaining > 0:
        last_second = second
        time_remaining = time_remaining - 1
        display.update_speed(badger2040.UPDATE_TURBO)
        display.thickness(3)
        display.pen(15)
        display.rectangle(130, 48, 64, 32)
        display.pen(0)
        display.text(
            str(time_remaining), # string: the text to draw
            145,            # int: x coordinate for the left middle of the text
            64,            # int: y coordinate for the left middle of the text
            scale=0.75,    # float: size of the text
            rotation=0.0  # float: rotation of the text in degrees
        )
        display.partial_update(
            130,  # int: x coordinate of the update region
            48,  # int: y coordinate of the update region (must be a multiple of 8)
            64,  # int: width of the update region
            32   # int: height of the 4update region (must be a multiple of 8)
        )
        
    if time_remaining <= 0:
        # Halt the Badger to save power, it will wake up if any of the front buttons are pressed
        display.halt()
        
    if changed and pin_string:
        display.update_speed(badger2040.UPDATE_NORMAL)
        display.thickness(1)

        print(pin_string)
        
        s_and_p = secret + pin_string
        print(s_and_p)
        secret_and_pin_hashed = binascii.hexlify(hashlib.sha256(str(secret + pin_string).encode()).digest())
        print(secret_and_pin_hashed)
        secret_and_pin_hashed_and_encoded = base64.b32encode(secret_and_pin_hashed).decode('utf-8')
        print(secret_and_pin_hashed_and_encoded)
        one_time_password = totp(time.time(), secret_and_pin_hashed_and_encoded, step_secs=60, digits=8)
        print(one_time_password)

        code = qrcode.QRCode()
        code.set_text("LOGIN+" + one_time_password[0])
        
        time_remaining = one_time_password[1]

        display.clear()

        max_size = min(128, 128)

        size, module_size = measure_qr_code(max_size, code)
        left = int((128 // 2) - (size // 2))
        top = int((128 // 2) - (size // 2))
        draw_qr_code(left, top, max_size, code)
        
        draw_button_text()

        display.update()
        pin_string = ''
            
        changed = False

    time.sleep(0.01)
