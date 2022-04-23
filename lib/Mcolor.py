import cv2
import numpy as np

class Mcolor:
    def __init__(self,
        basecolor=[32,32,128],
        angle_increment=30):

        self.bc = cv2.cvtColor(
            np.uint8([[basecolor]]),
            cv2.COLOR_RGB2HSV
            )[0][0]
        self.angle_increment = angle_increment
    def get(self, it):
        _ = self.bc
        _[0] += self.angle_increment * it
        return _.tolist()

if __name__ == "__main__":
    m = Mcolor()
    for i in range(10):
        print(m.get(i))
