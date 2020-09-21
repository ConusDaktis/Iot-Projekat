import sense_hat
from sense_hat import SenseHat
import time
from enum import Enum


class Colors(Enum):
    Green = (0, 255, 0)
    Yellow = (255, 255, 0)
    Blue = (0, 0, 255)
    Red = (255, 0, 0)
    White = (255, 255, 255)
    Nothing = (0, 0, 0)
    Pink = (255, 105, 180)
    Orange = (255, 165, 0)


class DisplayManager(object):
    def __andjela(self):
        W = Colors.White.value
        B = Colors.Blue.value
        N = Colors.Nothing.value
        logo = [
            N, N, N, N, N, N, N, N,
            N, N, N, B, B, N, N, N,
            N, N, B, N, N, B, N, N,
            N, B, N, N, N, N, B, N,
            N, B, N, N, N, N, B, N,
            N, B, B, B, B, B, B, N,
            N, B, N, N, N, N, B, N,
            N, B, N, N, N, N, B, N,
        ]
        return logo

    def __dusan(self):
        W = Colors.White.value
        B = Colors.Blue.value
        N = Colors.Nothing.value
        logo = [
            N, N, N, N, N, N, N, N,
            N, B, B, B, B, B, N, N,
            N, N, B, N, N, N, B, N,
            N, N, B, N, N, N, B, N,
            N, N, B, N, N, N, B, N,
            N, N, B, N, N, N, B, N,
            N, B, B, B, B, B, N, N,
            N, N, N, N, N, N, N, N,
        ]
        return logo

    def __unknown(self):
        N = Colors.Nothing.value
        R = Colors.Red.value
        logo = [
            N, N, N, R, R, N, N, N,
            N, N, R, N, N, R, N, N,
            N, R, N, N, N, N, R, N,
            N, R, N, N, N, N, R, N,
            N, N, R, N, N, R, N, N,
            N, N, N, N, R, N, N, N,
            N, N, N, N, N, N, N, N,
            N, N, N, N, R, N, N, N,
        ]
        return logo

    def __init__(self):
        self.s = SenseHat()
        self.s.low_light = True
        # Flash the raspberry pi logo at initialization
        self.__displayImage(self.__raspberry())
        time.sleep(1)
        self.s.clear()

    def __displayImage(self, image):
        self.s.set_pixels(image)

    def displayImage(self, strImage):
        print("Displaying " + strImage)
        if 'andjela arsovic' in strImage.lower():
            self.__displayImage(self.__andjela())
        elif 'dusan stokic' in strImage.lower():
            self.__displayImage(self.__dusan())
        elif 'none' in strImage.lower():
            self.s.clear()
        else:
            self.__displayImage(self.__unknown())
            self.s.clear()
