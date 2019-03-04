import gesture_detection
import localizer
import movement
from camera_module import camera_thread

cam_front = camera_thread(0)
cam_down = camera_thread(1)
cam_front.start()
cam_down.start()


def hit_flare(cur_pos):
    fwd_count = 25  # around 5 sec
    bwd_count = 15  # around 3 sec
    ok_to_go = False
    while True:
        img_front = cam_front.read()
        img_down = cam_down.read()
        coords_front = gesture_detection.get_coord_from_detection(img_front)
        cur_pos[0], cur_pos[1], cur_pos[2] = localizer.get_pos(img_down, cur_pos[0], cur_pos[1], cur_pos[2])
        x, y = coords_front[0], coords_front[1]
        if x < 700:
            movement.turn_right()
            continue
        elif x > 800:
            movement.turn_left()
            continue
        elif coords_front[3] >= 200:  # change this after testing
            ok_to_go = True
        if ok_to_go is True and fwd_count is not 0:
            movement.move_fwd()
            fwd_count -= 1
        elif bwd_count is not 0:
            movement.move_bwd()
            bwd_count -= 1
        else:
            img_down = cam_down.read()
            return localizer.get_pos(img_down, cur_pos[0], cur_pos[1], cur_pos[2])
