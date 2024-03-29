import time
import cv2
import movement
import depthdetect
from camera_module import camera_thread
import gesture_detection

camera_front = camera_thread(0)
camera_front.start()
camera_down = camera_thread(1)
camera_down.start()
while True:
    height = depthdetect.get_depth(camera_down.read())
    if height > 1.5:
        movement.move_down()
    else:
        break
fwd_count = 25
find_count = 25
while True:
    t1 = time.time()
    img = camera_front.read()
    img_down = camera_down.read()
    coords = gesture_detection.get_coord_from_detection(img)
    # x,y,width,height,category
    cv2.imshow('pass_gate_img', img)
    print(coords)
    if find_count and len(coords) is 0:
        movement.turn_left()
        find_count -= 1
    elif len(coords) is 0:
        movement.turn_right()
    elif len(coords) is 2 and coords[0][4] is 0:
        x1, x2, y1, y2 = coords[0][0], coords[1][0], coords[0][1], coords[1][1]
        if ((x1 + x2) // 2) < 800:
            movement.turn_left()
            continue
        elif ((x1 + x2) // 2) > 720:
            movement.turn_right()
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
