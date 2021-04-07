import numpy as np
import sda_path

x = np.array([0,0])
y = np.array([10,0])
z = np.array([5,5])

path = sda_path.Path(5)
points_set = path.spline_it(x, y, z)
for s in points_set:
    for point in s:
        print point
    print ""

