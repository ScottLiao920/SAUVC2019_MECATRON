import time
import cv2
import movement
import localizer
from camera_module import camera_thread
import gesture_detection

camera_front = camera_thread(0)
camera_front.start()
camera_down = camera_thread(1)
camera_down.start()


def pass_gate(cat, pos):
    fwd_count = 25
    while True:
        t1 = time.time()
        img = camera_front.read()
        img_down = camera_down.read()
        pos[0], pos[1], pos[2] = localizer.get_pos(img_down, pos[0], pos[1], pos[2])
        coords = gesture_detection.get_coord_from_detection(img)
        # x,y,width,height,category
        cv2.imshow('pass_gate_img', img)
        print(coords)
        movement.turn_left()
        if len(coords) is 2 and coords[0][4] is cat:
            x1, x2, y1, y2 = coords[0][0], coords[1][0], coords[0][1], coords[1][1]
            if not 700 < ((x1 + x2) // 2) < 800:
                movement.turn_left()
                continue
            if not 100 < ((y1 + y2) // 2) < 200:
                if (y1 + y2) // 2 < 100:
                    movement.move_up()
                    continue
                else:
                    movement.move_down()
                    continue
            movement.move_fwd()
            if (coords[0][3] + coords[1][3]) // 2 > 180:
                if fwd_count:
                    fwd_count -= 1
                    movement.move_fwd()
                else:
                    movement.stop()
                break
        t2 = time.time()
        print("fps:", 1 / (t2 - t1))
    print("Gate passed!")
    camera_front.release()
    return True
