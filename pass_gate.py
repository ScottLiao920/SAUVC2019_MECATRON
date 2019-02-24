import time
import movement
import gesture_detection


def pass_gate(img, cat):
    while True:
        coords = gesture_detection.get_coord_from_detection(img)
        # x,y,width,height,category
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
            time.sleep(2)
            if (coords[0][3] + coords[1][3]) // 2 > 180:
                time.sleep(5)
                movement.stop()
                break
    print("Gate passed!")
    return True
