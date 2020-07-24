import numpy as np

# This function maps the gamepad joystick's control values to a point in the region [0,1] X [0,1] in R^2
def map_to_unit_interval(x, y):
    # The equation for the conversion of a single value k in the integer interval [0..255] to the real interval [0, 1] is f(k) = ((k-128)^2 / 128^2)
    # The k value 0 is given when the gamepad's joystick is totally upwards in the y axis and totally to the right in the x axis 
    # if(x < 0):
    #     x = 0
    # elif()
    Px = ((float(x)-128.0)*(float(x)-128.0))/(128.0*128.0)
    Py = ((float(y)-128.0)*(float(y)-128.0))/(128.0*128.0)
    
    # It returns a 2D numpy array with the converted values
    return np.array([Px, Py])

# This function calculates the amount of the PWM that have to be discounted in order for the prototipe to turn sideways
def calculate_steering_discount(pwmPoint):
    # This amount is calculated through the angle that the vector returned by the function map_to_unit_interval makes with the x axis 
    aux = (1.0 - abs(np.arctan2(pwmPoint[1], pwmPoint[0])/(np.pi/2.0)))
    if(aux > 0.75):
        aux = 0.75
    return aux
    #return (np.arctan2(pwmPoint[1], pwmPoint[0])/2.0)
    #return ((1.0 - abs(np.arctan2(pwmPoint[1], pwmPoint[0])/(np.pi/2.0)))*0.75)

# Simple function to be certain that the min value for the PWM is the min valid one, in this case 0
def round_to_0_if_smaller(x):
    if(x < 0):
        return 0.0
    else:
        return x

# Simple function to be certain that the max value for the PWM is the max valid one, in this case 1
def round_to_1_if_greater(x):
    if(x > 1):
        return 1.0
    else:
        return x
