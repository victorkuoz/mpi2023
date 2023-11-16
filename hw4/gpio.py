import RPi.GPIO as GPIO
import time

class LightSender(object):
    def __init__(self, pin = 22, preamble = "10101010", st = 1.0):
        self.pin = pin
        self.preamble = preamble
        self.st = st    # sleep time

        # to use Raspberry Pi board pin numbers
        GPIO.setmode(GPIO.BCM) # choose Bcm for convinent

        # set up GPIO output channel, we set GPIO4 (Pin 22) to OUTPUT
        GPIO.setup(self.pin, GPIO.OUT)

    def encode(self, msg):
        byte_string_list = []
        for c in msg:
            byte_string = bin(ord(c))[2:] # change c to ASCII int ord and bin format str without leading '0b'

            while len(byte_string) < 8: # append to 8-bits format
                byte_string = '0' + byte_string
            byte_string_list.append(byte_string)

        return byte_string_list

    # blinking one bit signal for st sec
    def blink(self):
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(self.st)
        GPIO.output(self.pin, GPIO.LOW)

    def blink_byte_string(self, byte_string):
        print(f'sending: ', end='')
        for ch in byte_string:
            if ch == '1':
                self.blink()
                print('1', end='', flush=True)
            else :
                print('0', end='', flush=True)
                time.sleep(self.st)
        print()

    def blink_preamble(self):
        self.blink_byte_string(self.preamble)

    def blink_integer(self, length):
        # from decimal to binary
        byte_string = ""
        for _ in range(8):
            if (length % 2) == 1:
                byte_string = '1' + byte_string
            else:
                byte_string = '0' + byte_string
            length //= 2

        self.blink_byte_string(byte_string)

    def blink_msg(self, msg):
        for byte_string in self.encode(msg):
            self.blink_byte_string(byte_string)

if __name__ == '__main__':
    try:
        gpio = LightSender(st=0.5)
        msg = input("Type the message: ")

        gpio.blink_preamble()
        gpio.blink_integer(len(msg))
        gpio.blink_msg(msg)
        gpio.blink_integer(gpio.checksum(msg))
    except KeyboardInterrupt:
        print("Stop!!!")
    finally:
        GPIO.cleanup()
