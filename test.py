import time

import gesture_detection
from camera_module import camera_thread

camera_thread = camera_thread(0)
camera_thread.start()

while True:
    t1 = time.time()
    img = camera_thread.read()
    coords = gesture_detection.get_coord_from_detection(img)
    # print (coords)
    t2 = time.time()
    print(coords, len(coords), ' fps: ', 1 / (t2 - t1))
