from modules.sda_geometry import *


x = Point(-1, 0, 0)
y = Point(1, 0, 0)
l = Line(x, y)
test_p = Point(0, 1, 0)

print l.distance(test_p)