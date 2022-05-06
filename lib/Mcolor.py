import cv2
import numpy as np

class Mcolor:
    def __init__(self,
        basecolor=[3,7,255],
        angle_increment=360/5):

        self.bc = cv2.cvtColor(
            np.uint8([[basecolor]]),
            cv2.COLOR_RGB2HSV
            )[0][0]
        self.angle_increment = angle_increment
    def get(self, it):
        _ = self.bc
        _[0] += self.angle_increment * it
        return cv2.cvtColor([[_]], cv2.COLOR_HSV2RGB)

if __name__ == "__main__":
    m = Mcolor()
    for i in range(10):
        print(m.get(i))
