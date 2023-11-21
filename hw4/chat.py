import RPi.GPIO as GPIO
import os

from threading import Timer
from gpio import LightSender
from light_sensor import GroveLightSensor

def cls():
    print ("\033[A                             \033[A")

class Chat(object):
    def __init__(self, ack = '11100000', preamble = '10101010', st = 1.0, syn = '11000000', threshold = 100, timeout = 3):
        self.keep_waiting = True
        self.sender = LightSender(ack = ack, st=st, syn=syn, preamble=preamble)
        self.sensor = GroveLightSensor(ack = ack, st=st, syn = syn, preamble=preamble)
        self.threshold = threshold
        self.timeout = timeout
        self.timer = Timer(self.timeout, self.timeout_handler)
        self.preamble = preamble

    def timeout_handler(self):
        self.keep_waiting = False

    def checksum(self, msg):
        return sum(ord(ch) for ch in msg) % 256

    def sending_mode(self):
        try:
            print("-----Sending mode-----")

            # handshaking
            while True:
                print('Handshaking...')
                print('Sending synchronize...')
                self.sender.synchronize()   # syn

                # set timer
                self.keep_waiting = True
                self.timer = Timer(self.timeout, self.timeout_handler)
                self.timer.start()

                # busy waiting ack
                while self.keep_waiting:
                    if self.threshold <= self.sensor.light:
                        self.timer.cancel()
                        break

                # timeout
                if self.keep_waiting == False:
                    input('Timeout!!!\nKeep handshaking with "Enter" / Quit with "Ctrl-C"\n')
                    cls()
                    continue

                print('Receiving acknowledge...')
                # not ack
                if self.sensor.detect_acknowledge() == False:
                    input('Wrong acknowledge!!!\nKeep handshaking with "Enter" / Quit with "Ctrl-C"\n')
                    cls()
                    continue

                print('Handshake success!!!')
                break

            msg = input("Type the message: ")
            checksum = self.checksum(msg)

            while True:
                print('Sending message...')
                # sending message
                self.sender.send_preamble()
                self.sender.send_value(len(msg))
                self.sender.send_msg(msg)
                self.sender.send_value(checksum)

                # set timer
                self.keep_waiting = True
                self.timer = Timer(self.timeout, self.timeout_handler)
                self.timer.start()

                # busy waiting ack
                print('Detecting acknowledge...')
                while self.keep_waiting:
                    if self.threshold <= self.sensor.light:
                        self.timer.cancel()
                        break

                # timeout
                if self.keep_waiting == False:
                    input('Timeout!!!\nQuit with "Ctrl-C"\n')
                    cls()

                if self.sensor.detect_acknowledge():
                    break
                input('Wrong acknowledge!!!\nResend with "Enter" / Quit with "Ctrl-C"\n')
                cls()

            print('Completed!!!')
        except KeyboardInterrupt:
            print("\nStopping sending...")
        finally:
            pass

    def receiving_mode(self):
        try:
            print("-----Receiving mode-----")
            while True:
                print("Handshaking...")
                # busy sensing
                while self.sensor.light < self.threshold:
                    continue

                print('Receiving synchronize...')
                # receive syn
                if not self.sensor.detect_synchronize():
                    print('Wrong synchronize!!!')
                    continue

                # send ack
                print('Sending acknowledge...')
                self.sender.acknowledge()
                print('Handshake success!!!')
                break

            while True:
                # busy waiting
                while self.sensor.light < self.threshold:
                    continue

                print('Receiving message...')
                self.sensor.detect_preamble()   # ignore
                length, msg = self.sensor.decode_value(self.sensor.detect_byte()), ''
                for _ in range(length):
                    msg += self.sensor.decode_char(self.sensor.detect_byte())

                recv_checksum = self.sensor.decode_value(self.sensor.detect_byte())
                if recv_checksum != self.checksum(msg):
                    self.sender.send_preamble()
                    self.sender.send_preamble() # wrong acknowledge
                    print("Wrong checksum...Rereceive!!!")
                    continue

                print('Sending acknowledge...')
                self.sender.acknowledge()
                print(f'Completed!!!\nReceive msg: {msg}')
                break
        except KeyboardInterrupt:
            print("\nStopping receiving...")
        finally:
            pass

def main():
        try:
            chat = Chat(st=0.5, threshold=250)

            os.system('clear')
            print('Welcome to MpiChat')
            while True:
                cmd = input('Send message with command "s" / Receive message with command "r" / Quit with command "Ctrl-C"\n')
                if cmd == 's':
                    cls()
                    chat.sending_mode()
                elif cmd == 'r':
                    cls()
                    chat.receiving_mode()
                else:
                    cls()
                    print('Wrong command!!!')
        except KeyboardInterrupt:
            pass
        finally:
            GPIO.cleanup()
            print('\nBye~')

if __name__ == "__main__":
    main()