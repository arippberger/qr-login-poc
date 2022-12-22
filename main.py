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

def a_button_callback(pin):
    global pin_string
    pin_string += 'a'
    print(pin_string)
    
def b_button_callback(pin):
    global pin_string
    pin_string += 'b'
    print(pin_string)
    
def c_button_callback(pin):
    global pin_string
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


changed = not badger2040.woken_by_button()


while True:
        
    if display.pressed(badger2040.BUTTON_UP): 
        pin_string = ''
        time.sleep_ms(250)
        
    if display.pressed(badger2040.BUTTON_DOWN):
        changed = True
        
    if changed:

        print(pin_string)
        
        s_and_p = secret + pin_string
        
        print(s_and_p)
        
        secret_and_pin_hashed = binascii.hexlify(hashlib.sha256(str(secret + pin_string).encode()).digest())
        
        print(secret_and_pin_hashed)
        
        secret_and_pin_hashed_and_encoded = base64.b32encode(secret_and_pin_hashed).decode('utf-8')
        
        print(secret_and_pin_hashed_and_encoded)
        
        one_time_password = totp(time.time(), secret_and_pin_hashed_and_encoded, step_secs=30, digits=8)
        
        print(one_time_password)

        code = qrcode.QRCode()
        code.set_text("LOGIN+" + one_time_password[0])

        display.clear()

        max_size = min(128, 128)

        size, module_size = measure_qr_code(max_size, code)
        left = int((128 // 2) - (size // 2))
        top = int((128 // 2) - (size // 2))
        draw_qr_code(left, top, max_size, code)

        display.update()
        pin_string = ''
        changed = False

    # Halt the Badger to save power, it will wake up if any of the front buttons are pressed
    display.halt()
