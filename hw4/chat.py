import RPi.GPIO as GPIO
import time
import os

from threading import Timer
from gpio import LightSender
from light_sensor import GroveLightSensor

class Chat(object):
    def __init__(self, st = 1.0, threshold = 100, timeout = 3, preamble = '10101010'):
        self.keep_waiting = True
        self.sender = LightSender(st=st, preamble=preamble)
        self.sensor = GroveLightSensor(st=st, preamble=preamble)
        self.threshold = threshold
        self.timeout = timeout
        self.timer = Timer(self.timeout, self.timeout_handler())
        self.preamble = preamble

    def timeout_handler(self):
        self.keep_waiting = False

    def checkSum(self, msg):
        encode_msg = self.sender.encode(msg)
        binary_sum = sum(int(e, 2) for e in encode_msg)
        # print(binary_sum)
        binary_sum = format(binary_sum, 'b')
        # print(binary_sum)

        if(len(binary_sum) > 8):
            binary_sum = binary_sum[-8:]

        if(len(binary_sum) < 8):
            binary_sum = '0' * (8 - len(binary_sum)) + binary_sum

        return binary_sum 

    def sending_mode(self):
        try:
            print("-----Sending mode-----")
            while True:
                print("Connecting...")
                self.sender.blink_preamble()

                self.keep_waiting = True
                self.timer = Timer(self.timeout, self.timeout_handler)
                self.timer.start()

                while self.keep_waiting: # busy waiting
                    if self.threshold <= self.sensor.light:
                        self.timer.cancel()
                        break

                if self.keep_waiting == False:
                    print("Timeout, connection refused!!!")
                    continue

                if self.sensor.detect_preamble() == False:
                    print("Handshake Failed!!!")
                    continue

                msg = input("Type the message: ")

                while True:
                    print('Sending message...')
                    checksum = self.checkSum(msg)
                    self.sender.blink_preamble()
                    self.sender.blink_integer(len(msg))
                    self.sender.blink_msg(msg)
                    # blink checksum
                    print(f"send checksum: {checksum}")
                    self.sender.blink_byte_string(checksum)

                    print('Waiting acknowledge...')
                    while self.sensor.light < self.threshold:
                        continue

                    if self.sensor.detect_byte() == self.preamble:
                       break
                    print('Mission failed: Retrying...')

                print('Mission completed')

        except KeyboardInterrupt:
            cmd = input("\nExit the program with 'e' / Change to sensing mode with 's'\n")
            if cmd == "e":
                GPIO.cleanup()
                os._exit(0)

            print("Stopping sending...")
            time.sleep(0.5)
            self.sensing_mode()
        finally:
            pass

    def sensing_mode(self):
        try:
            print("-----Sensing mode-----")
            while True:
                print('Sensing...')
                while self.sensor.light < self.threshold:
                    continue

                if not self.sensor.detect_preamble():
                    print('Preamble error!')
                    continue

                self.sender.blink_preamble()

                while True:
                    print("detecing message...")
                    while self.sensor.light < self.threshold:
                        continue

                    self.sensor.detect_preamble()   # ignore

                    length, msg = self.sensor.decode_integer(self.sensor.detect_byte()), ''
                    for _ in range(length):
                        msg += self.sensor.decode_byte(self.sensor.detect_byte())

                    recv_checksum = self.sensor.decode_integer(self.sensor.detect_byte())
                    print(f"receive checksum: {recv_checksum}")
                    real_checksum = int(self.checkSum(msg), 2)
                    print(f"calculated checksum: {real_checksum}")
                    if recv_checksum == real_checksum:
                        print("checksum pass")
                    else:
                        print("checksum fail")
                        self.sender.blink_byte_string('11110000')
                        continue
                    # if checksum fail...
                        # continue

                    self.sender.blink_preamble()
                    print(f'Receive msg: {msg}')
                    break

        except KeyboardInterrupt:
            cmd = input("\nExit the program with 'e' / Change to sending mode with 's'\n")
            if cmd == "e":
                os._exit(0)

            print("Stopping sensing...")
            time.sleep(0.5)
            self.sending_mode()
        finally:
            pass

def main():
    chat = Chat(st=0.5)

    cmd = input("Sensing with command 'sensing' / Sending with command 'sending'...\n")
    if cmd == 's':
        chat.sensing_mode()
    else:
        chat.sending_mode()

if __name__ == "__main__":
    main()