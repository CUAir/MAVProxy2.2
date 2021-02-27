#!/usr/bin/env python
import math


def heading_to_vector(heading, speed):
    float_heading = float(heading)
    float_speed = float(speed)
    vx = float_speed * math.cos(math.degrees(float_heading + 90))
    vy = float_speed * math.sin(math.degrees(float_heading + 90))
    return vx, vy


# Converts from 0 -> 360 to -pi -> +pi
def degrees_to_rads(degrees):
    return (degrees * math.pi / 180.0) - math.pi


def str_to_bool(string):
    if string in ['True', 'true', 't', 'TRUE', 'T', True]:
        return True
    elif string in ['False', 'false', 'f', 'FALSE', 'F', False]:
        return False
    else:
        raise ValueError("String is not a boolean")

def isFloat(string):
    try: 
        float(string)
        return True
    except:
        return False
