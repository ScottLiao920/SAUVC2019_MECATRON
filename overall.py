# Explanation:
# pass_gate first
# Move inside main arena in S shape
# Detect any objects from front camera will go aim for it
# Possible bugs: x and y constraints


import time

import flare_hitting
import gesture_detection
import localizer
import movement
from pass_gate import pass_gate
import target_zone
from camera_module import camera_thread

print("Connected!")
total_col = 28
total_row = 25
green_cloth_pos = (1, 3)
cur_pos = (0, 0, 2)
flare_completed = False
ball_picked_up = False
left = False
right = True  # For overall movement

# need to change according to starting point:
start2right = 10  # need to change this constant according to distance from starting point to right side wall

movement.move_down()
time.sleep(2)
camera_front = camera_thread(0)
camera_down = camera_thread(1)
# initialize parameters

cur_pos = pass_gate.pass_gate(cur_pos)
# go through the gate
camera_down.start()
camera_front.start()
while True:
    # cur_pos in the form of x,y,z
    t1 = time.time()
    img_front = camera_front.read()
    img_down = camera_down.read()
    print("Detecting!")
    cur_pos[0], cur_pos[1], cur_pos[2] = localizer.get_pos(img_down, cur_pos[0], cur_pos[1], cur_pos[2])
    if cur_pos[2] < 0.5:
        movement.move_up()
        time.sleep(1)
        continue
    coords_front = gesture_detection.get_coord_from_detection(img_front)
    print(coords_front)
    t2 = time.time()
    print("fps:", 1 / (t2 - t1))
    if len(coords_front) is not 0:
        x, y, cat = coords_front[0][0], coords_front[0][1], coords_front[0][4]
        if cat is 2:
            # flare detected
            camera_down.release()
            camera_front.release()
            cur_pos[0], cur_pos[1], cur_pos[2] = flare_hitting.hit_flare(cur_pos)
            camera_down.start()
            camera_front.start()
            flare_completed = True
        if cat is 3:
            # target zone detected
            # release these cameras from this function to use ins
            camera_down.release()
            camera_front.release()
            cur_pos[0], cur_pos[1], cur_pos[2] = target_zone.ball_play(cur_pos)
            camera_down.start()
            camera_front.start()
            ball_picked_up = True
    else:
        # No target detected
        '''
        if cur_pos[0] > 10 and cur_pos[1] < 2:
            movement.turn_right()
        if cur_pos[1] > 21 or cur_pos[0] > start2right:
            movement.turn_right()
        elif cur_pos[0] > 10 and cur_pos[1] < 2:
            movement.turn_right()
        else:
            movement.move_fwd()
        '''
        if cur_pos[0] > start2right and cur_pos[1] < 8:
            movement.move_fwd()
            left = True
            right = False
        elif cur_pos[0] < -start2right and cur_pos[1] < 16:
            movement.move_fwd()
            left = False
            right = True
        elif left:
            movement.turn_left()
        elif right:
            movement.turn_right()
    if flare_completed and ball_picked_up:
        movement.move_up()
