import cv2
import math
import numpy as np
from tiles import Tile
import time
import random


def img_correction(img):
    clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(5, 5))
    res = np.zeros_like(img)
    for i in range(3):
        res[:, :, i] = clahe.apply(img[:, :, i])
    return res


def rand_color():
    a = random.randrange(0, 256)
    b = random.randrange(0, 256)
    c = random.randrange(0, 256)
    return np.array([a, b, c])


def predict_depth(img):
    if area < 10:
        return 0
    # fov of camera
    fov_w, fov_h = 48 * math.pi / 180, 36 * math.pi / 180
    px_W, px_H = 640, 480

    # tile real world dimension
    real_w, real_h = 0.25, 0.12

    # pixel tile size
    px_w = math.sqrt(area / (real_w * real_h)) * real_w
    px_h = math.sqrt(area / (real_w * real_h)) * real_h
    # print(px_w, px_h)

    # camera fov in meters
    W = px_W * real_w / px_w
    H = px_H * real_h / px_h
    # print(W, H)
    # predict depth
    d_w = W / (2 * math.tan(fov_w / 2))
    d_h = H / (2 * math.tan(fov_h / 2))
    # print(d_w, d_h)
    return (d_w + d_h) / 2


switch_init = False  # wait for armed state from estop
last_disarm_time = 0
arming_count = 0

frame_counter = 0
ind_count = 0

pos_x = 0
pos_y = 0

last_yaw = 0
last_height = 1.5

last_yaw_count = 0

tiles = []
colors = []

for i in range(20):
    colors.append(rand_color())

grad_pred = []
height_pred = []

imu_roll = 0
imu_pitch = 0
imu_yaw = 0

first = True

# stores absolute imu direction of pool frame, if not avail set to 0
yaw_init_offset = 0  # 125*math.pi/180

with_visual_correction = True
start_time = time.time()
# print(len(self.tiles))
font = cv2.FONT_HERSHEY_SIMPLEX
color = (0, 0, 255)


def get_pos(img, pos_x, pos_y, depth):
    res = img.copy()
    h, w = img.shape[:2]

    M = cv2.getRotationMatrix2D((w / 2, h / 2), (imu_yaw) * 180 / math.pi, 1)
    img = cv2.warpAffine(img, M, (w, h))

    # circle mask
    circle_mask = np.zeros_like(img)
    circle_mask = cv2.circle(circle_mask, (int(w / 2), int(h / 2)), int(h / 2), [255, 255, 255], -1)
    circle_mask = circle_mask[:, :, 0]

    # print(h,w)
    img = img_correction(img)

    blur = cv2.GaussianBlur(img, (7, 7), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    mask = cv2.adaptiveThreshold(hsv[:, :, 2], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                 cv2.THRESH_BINARY, 21, 2)

    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    opening = 255 - opening
    opening = cv2.dilate(opening, None, iterations=1)
    contour_mask = 255 - opening
    opening[circle_mask == 0] = 0
    # fit lines to extract major direction
    minLineLength = 100
    lines = cv2.HoughLinesP(image=opening, rho=1, theta=np.pi / 180,
                            threshold=100, lines=np.array([]), minLineLength=minLineLength, maxLineGap=12)

    grad = np.zeros((len(lines), 1))
    i = 0
    for line in lines:
        # find two major gradients
        x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
        theta = math.atan(float(y2 - y1) / (x2 - x1)) * 180 / math.pi

        grad[i] = theta
        i += 1
        # cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3, cv2.LINE_AA)
        cv2.line(contour_mask, (x1, y1), (x2, y2), 0, 1, cv2.LINE_AA)

    hist, bin_edges = np.histogram(grad, density=False)
    ind = np.argmax(hist)
    best_grad = round((bin_edges[ind] + bin_edges[ind + 1]) / 2, 2)

    ind = np.where(np.abs(grad - best_grad) < 10)
    good_grads = grad[ind]
    best_grad = np.mean(good_grads)

    # contour_mask=self.mask_correction(contour_mask)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), best_grad, 1)
    contour_mask = cv2.warpAffine(contour_mask, M, (w, h))

    (contours, _) = cv2.findContours(contour_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour_mask = cv2.cvtColor(contour_mask, cv2.COLOR_GRAY2BGR)
    areas = []
    border = 0
    r = []

    for contour in contours:
        rect = cv2.boundingRect(contour)

        if rect[0] > border and rect[0] + rect[2] < w - border and rect[1] > border and rect[3] + rect[1] < h - border:
            area = int(rect[3] * rect[2])
            # print(area)
            ar = float(rect[2]) / rect[3]
            real_ar = 0.25 / 0.12
            if area > 1000 and area < 120000 and abs(ar / real_ar - 1) < 0.3:
                cv2.rectangle(contour_mask, (rect[0], rect[1]), (rect[2] + rect[0], rect[3] + rect[1]), (0, 255, 0), 2)
                areas.append(area)
                r.append(rect)

    areas = np.asarray(areas)
    hist, bin_edges = np.histogram(areas, bins='fd', density=False)
    ind = np.argmax(hist)
    # best_area=(bin_edges[ind]+bin_edges[ind+1])/2

    best_area = round((bin_edges[ind] + bin_edges[ind + 1]) / 2, 2)
    ind = np.where(np.abs(areas - best_area) < 0.1 * best_area)
    if len(ind) > 5:
        good_areas = areas[ind]
        best_area = np.mean(good_areas)

    pred_depth = predict_depth(best_area)

    pred_depth = pred_depth * math.cos(imu_pitch) * math.cos(imu_roll)

    for tile in tiles:
        r = tile.one_step_update(r)

    for rect in r:
        tiles.append(Tile(rect, ind_count))
        ind_count += 1

    for tile in tiles:
        if tile.alive == False:
            tiles.remove(tile)

    del_x = []
    del_y = []
    for tile in tiles:
        color = colors[tile.ind % 20]
        color = tuple([int(x) for x in color])
        if len(tile.centers) > 2:
            del_x.append(tile.centers[-1][1] - tile.centers[-2][1])
            del_y.append(tile.centers[-1][0] - tile.centers[-2][0])
        contour_mask = cv2.circle(contour_mask, (int(tile.centers[-1][0]), int(tile.centers[-1][1])), 5, color, -1)
        cv2.putText(contour_mask, str(tile.ind), (tile.bb[0] + 10, tile.bb[1] + 10), font, 0.8, color, 1, cv2.LINE_AA)

    hist, bin_edges = np.histogram(np.asarray(del_x), bins='fd', density=False)
    ind = np.argmax(hist)
    best_del_x = round((bin_edges[ind] + bin_edges[ind + 1]) / 2, 2)

    hist, bin_edges = np.histogram(np.asarray(del_y), bins='fd', density=False)
    ind = np.argmax(hist)
    best_del_y = round((bin_edges[ind] + bin_edges[ind + 1]) / 2, 2)

    # tile real world dimension
    fov_w, fov_h = 48 * math.pi / 180, 36 * math.pi / 180
    px_W, px_H = 640, 480
    W = 2 * pred_depth * math.tan(fov_w / 2) + 0.0001
    ppm = px_W / W
    pos_x -= best_del_x / ppm
    pos_y -= best_del_y / ppm
    return pos_x, pos_y, pred_depth
