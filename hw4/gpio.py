import RPi.GPIO as GPIO
import time

class LightSender(object):
    def __init__(self, ack = '11100000', pin = 22, preamble = "10101010", st = 1.0, syn = '11000000'):
        self.ack = ack
        self.pin = pin
        self.preamble = preamble
        self.st = st    # sleep time
        self.syn = syn

        # to use Raspberry Pi board pin numbers
        GPIO.setmode(GPIO.BCM) # choose Bcm for convinent

        # set up GPIO output channel, we set GPIO4 (Pin 22) to OUTPUT
        GPIO.setup(self.pin, GPIO.OUT)

    def encode(self, msg):
        byte_list = []
        for c in msg:
            byte = bin(ord(c))[2:] # change c to ASCII int ord and bin format str without leading '0b'

            while len(byte) < 8: # append to 8-bits format
                byte = '0' + byte
            byte_list.append(byte)
        return byte_list

    # blinking one bit signal for st sec
    def blink(self):
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(self.st)
        GPIO.output(self.pin, GPIO.LOW)

    def send_byte(self, byte):
        print(f'sending: ', end='')
        for ch in byte:
            if ch == '1':
                print('1', end='', flush=True)
                self.blink()
            else :
                print('0', end='', flush=True)
                time.sleep(self.st)
        print()

    def send_preamble(self):
        self.send_byte(self.preamble)
    
    def synchronize(self):
        self.send_preamble()
        self.send_byte(self.syn)

    def acknowledge(self):
        self.send_preamble()
        self.send_byte(self.ack)

    def send_value(self, value):
        # from decimal to binary
        byte_string = ""
        for _ in range(8):
            if (value % 2) == 1:
                byte_string = '1' + byte_string
            else:
                byte_string = '0' + byte_string
            value //= 2
        self.send_byte(byte_string)

    def send_msg(self, msg):
        for byte in self.encode(msg):
            self.send_byte(byte)

if __name__ == '__main__':
    try:
        gpio = LightSender(st=0.5)
        msg = input("Type the message: ")

        gpio.send_preamble()
        gpio.send_value(len(msg))
        gpio.send_msg(msg)
    except KeyboardInterrupt:
        print("Stop!!!")
    finally:
        GPIO.cleanup()
