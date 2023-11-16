import time, sys
from grove.adc import ADC
from grove.helper import SlotHelper

class GroveLightSensor(object):
    '''
    Grove Light Sensor class
    '''
    def __init__(self, preamble = '10101010', st = 1.0, threshold = 100):
        self.adc = ADC()
        self.channel = SlotHelper(SlotHelper.ADC).argv2pin()
        self.preamble = preamble
        self.st = st   # sleep time
        self.threshold = threshold # brightness threshold

    @property
    def light(self):
        '''
        Get the light strength value, maximum value is 100.0%

        Returns:
            (int): ratio, 0(0.0%) - 1000(100.0%)
        '''
        return self.adc.read(self.channel)

    def detect_byte(self):  # output byte in string format
        byte_string = ""
        print('detecting: ', end='')
        for _ in range(8) :
            if self.light >= self.threshold:
                byte_string += '1'
            else :
                byte_string += '0'
            print(byte_string[-1], end='', flush=True)
            time.sleep(self.st)
        print()
        return byte_string

    def decode_byte(self, byte_string):
        ascii_val = int('0b' + byte_string, 2)    # change string (binary) to int (decimal)
        return chr(ascii_val)  # chr(65) == 'A'

    def decode_integer(self, byte_string):
        val = 0
        for _ in range(8):
            val <<= 1
            if byte_string[0] == '1':
                val += 1
            byte_string = byte_string[1:]
        return val

    def detect_preamble(self):
        return self.preamble == self.detect_byte()

if __name__ == '__main__':
    sensor = GroveLightSensor()

    print(sensor.decode_byte('00000101', False))
    print(sensor.decode_byte('01101000'))
    print(sensor.decode_byte('01100101'))
    print(sensor.decode_byte('01101100'))
    print(sensor.decode_byte('01101100'))
    print(sensor.decode_byte('01101111'))
    sensor.detect_byte()