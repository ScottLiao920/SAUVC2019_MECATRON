import time

import gesture_detection
import movement
import localizer
from camera_module import camera_thread

cam_front = camera_thread(0)
cam_down = camera_thread(1)
cam_front.start()
cam_down.start()


def ball_play(pos):
    arm_pos = False
    while True:
        img_down = cam_down.read()
        img_front = cam_front.read()
        coords_front = gesture_detection.get_coord_from_detection(img_front)
        coords_down = gesture_detection.get_coord_from_detection(img_down)
        pos[0], pos[1], pos[2] = localizer.get_pos(img_down, pos[0], pos[1], pos[2])
        if arm_pos is False:
            if len(coords_front) is not 0:
                x, y = coords_front[0], coords_front[1]
                if x < 700:
                    movement.turn_right()
                elif x > 800:
                    movement.turn_left()
                else:
                    movement.move_fwd()
                    time.sleep(1)
            elif len(cam_down) is not 0:
                x, y = coords_down[0], coords_down[1]
                if 300 < y < 700 and 600 < x < 900:
                    movement.arm()
                    arm_pos = True
                    movement.move_bwd()
                    time.sleep(10)
                    movement.move_fwd()
                    time.sleep(10)
                    # move out of target zone and move in again
                elif y > 700:
                    movement.move_bwd()
                else:
                    movement.move_fwd()
        else:
            if len(coords_down) is not 0:
                x, y = coords_down[0], coords_down[1]
                if 300 < y < 700 and 600 < x < 900:
                    movement.arm()
                    break
                elif y > 700:
                    movement.move_bwd()
                else:
                    movement.move_fwd()
    return pos[0], pos[1], pos[2]
