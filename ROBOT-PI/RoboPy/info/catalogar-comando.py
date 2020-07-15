#import evdev
from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event3')

#prints out device info at start
print(gamepad)
print(gamepad.capabilities(verbose=True,absinfo=True))

commands = {
            (3, 1): 'Ly',
            (3, 0): 'Lx', 
            (3, 5): 'Ry', 
            (3, 2): 'Rx',
            (1, 308): 'btn_Y',
            (1, 307): 'btn_X', 
            (1, 304): 'btn_A',
            (1, 305): 'btn_B',
            (1, 310): 'btn_LB',
            (1, 311): 'btn_RB',
            (3, 9): 'Rt',
            (3, 10): 'Lt',
            (0,0): 'sync'
            }

#evdev takes care of polling the controller in a loop
for event in gamepad.read_loop():
        print(event)
        print(categorize(event))
        print(event.code)
        print(event.value)
        print('\n')
        
        key = gamepad.active_keys()
        
        try:
                if(commands[(1, key[0])] == 'btn_X'):
                        print("\n\nRegressor OFF!\n\n")
        except (IndexError, KeyError, AttributeError) as error:
                pass
        
        print( "Botoes ativos: ", gamepad.active_keys(verbose=True))
