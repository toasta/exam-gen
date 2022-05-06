import colorsys

class Mcolor:
    def __init__(self, basecolor=[0,0,1], angle_increment=360/5):

        self.bc = colorsys.rgb_to_hsv(*basecolor)
        self.angle_increment = angle_increment

    def get(self, it):
        _ = self.bc
        tmp = colorsys.hsv_to_rgb(_[0] + self.angle_increment*it, _[1], _[2])
        return [ int(_ * 255) for _ in tmp]

if __name__ == "__main__":
    m = Mcolor()
    for i in range(10):
        print(m.get(i))
