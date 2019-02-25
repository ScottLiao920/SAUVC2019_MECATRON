# Explanation:
#
import time

import numpy as np

import depthdetect
import gesture_detection
import movement
import pass_gate
from camera_module import camera_thread

total_col = 28
total_row = 25
green_cloth_pos = (1, 3)
cur_pos = (0, 14)
# define serial port to communicate with myRio
'''ser = serial.Serial(
    port='/dev/ttyUSB0',  # Change port
    baudrate=115200,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS
)'''


def map_init():
    map = np.zeros([total_row, total_col])
    map[cur_pos[0]][cur_pos[1]] = 1
    for i in range(2):
        for j in range(8):
            map[i + green_cloth_pos[0]][j + green_cloth_pos[1]] = 1
    map[8] = 0
    print(map)


map_init()
camera_front = camera_thread(0)
# camera_down = camera_thread(1)
# camera_down.start()
camera_front.start()
img_front = camera_front.read()
pass_gate.pass_gate(1)
while True:
    # cur_pos in the form of x,y,z
    t1 = time.time()
    # img_front = camera_front.read()
    # img_down = camera_down.read()
    # cur_depth = depthdetect.get_depth(img_down)
    # if cur_depth < 1:
    # write to myrio to stop and move up
    # coords_front = gesture_detection.get_coord_from_detection(img_front)
    # print (coords)
    t2 = time.time()
    '''if not len(coords_front) is 0:
        x, y, cat = coords_front[0], coords_front[1], coords_front[4]
        if cat is 2:
        # flare detected
        # if x
        if cat is 3:
            # target zone detected
            # begin to detect blue drum using camera_down
            coords_down = gesture_detection.get_coord_from_detection(img_down)
        if cat is 0:
    # gate detected
    else:
        # No target detected
        movement.move_forward'''
    print("fps:", 1 / (t2 - t1))
    # if coords
