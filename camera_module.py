import threading
import time

import cv2


class camera_thread(threading.Thread):
    # camera_down = cv2.VideoCapture(0)
    # camera_up = cv2.VideoCapture(1)

    def __init__(self, camera_id):
        self.cap = cv2.VideoCapture(camera_id)
        # self.cap.set(14, 0.01)  #exposure
        _, self.img = self.cap.read()
        # self.img = hist_equal(self.img)
        threading.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(0.03)
            try:
                _, self.img = self.cap.read()
            # self.img = hist_equal(self.img)
            # equ= cv2.cvtColor(self.img, cv2.COLOR_BGR2HLS)
            # equ[:,:,1] = cv2.equalizeHist(equ[:,:,1])
            # self.img = cv2.cvtColor(equ, cv2.COLOR_HLS2BGR)
            except:
                pass

    def read(self):
        return self.img

    def release(self):
        self.release()
        cv2.destroyAllWindows()
        return True
