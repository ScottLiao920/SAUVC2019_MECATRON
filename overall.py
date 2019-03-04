# Explanation:
#
import time

import numpy as np

import gesture_detection
import localizer
import movement
import pass_gate
import target_zone
import flare_hitting
from camera_module import camera_thread

total_col = 28
total_row = 25
green_cloth_pos = (1, 3)
cur_pos = (0, 0, 2)
flare_completed = False
ball_picked_up = False

# need to change according to starting point:
start2right = 10  # need to change this constant according to distance from starting point to right side wall


def map_init():
    mapping = np.zeros([total_row, total_col])
    mapping[cur_pos[0]][cur_pos[1]] = 1
    for i in range(2):
        for j in range(8):
            mapping[i + green_cloth_pos[0]][j + green_cloth_pos[1]] = 1
    mapping[8] = 0
    print(mapping)


map_init()
camera_front = camera_thread(0)
camera_down = camera_thread(1)
camera_down.start()
camera_front.start()
img_front = camera_front.read()
# initialize parameters

pass_gate.pass_gate(1)
# go through the gate
while True:
    # cur_pos in the form of x,y,z
    t1 = time.time()
    img_front = camera_front.read()
    img_down = camera_down.read()
    cur_pos[0], cur_pos[1], cur_pos[2] = localizer.get_pos(img_down, cur_pos[0], cur_pos[1], cur_pos[2])
    # if cur_depth < 1:
    # write to myrio to stop and move up
    coords_front = gesture_detection.get_coord_from_detection(img_front)
    print(coords_front)
    t2 = time.time()
    if not len(coords_front) is 0:
        x, y, cat = coords_front[0], coords_front[1], coords_front[4]
        if cat is 2:
            # flare detected
            cur_pos[0], cur_pos[1], cur_pos[2] = flare_hitting.hit_flare(cur_pos)
            flare_completed = True
        if cat is 3:
            # target zone detected
            # release these cameras from this function to use ins
            cur_pos[0], cur_pos[1], cur_pos[2] = target_zone.ball_play(cur_pos)
            ball_picked_up = True
    else:
        # No target detected
        if cur_pos[0] > 10 and cur_pos[1] < 2:
            movement.turn_right()
        if cur_pos[1] > 21 or cur_pos[0] > start2right:
            movement.turn_right()
        elif cur_pos[0] > 10 and cur_pos[1] < 2:
            movement.turn_right()
        else:
            movement.move_fwd()
    if flare_completed and ball_picked_up:
        movement.move_up()
    print("fps:", 1 / (t2 - t1))
