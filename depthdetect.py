import math

import cv2
import numpy


def get_depth(img):
    h, w = img.shape[:2]

    # yaw_angle from imu
    yaw_angle = 0
    M = cv2.getRotationMatrix2D((w / 2, h / 2), yaw_angle * 180 / math.pi, 1)
    img = cv2.warpAffine(img, M, (w, h))
    circle_mask = numpy.zeros_like(img)
    circle_mask = cv2.circle(circle_mask, (int(w / 2), int(h / 2)), int(h / 2), [255, 255, 255], -1)
    circle_mask = circle_mask[:, :, 0]
    # cv2.imshow('test', img)
    # cv2.waitKey(0)
    clach = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(5, 5))
    newimg = numpy.zeros_like(img)
    for i in range(3):
        newimg[:, :, i] = clach.apply(img[:, :, i])
    cv2.imshow('123', newimg)
    blur = cv2.GaussianBlur(newimg, (7, 7), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    mask = cv2.adaptiveThreshold(hsv[:, :, 2], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 2)
    kernel = numpy.ones((5, 5), numpy.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    opening = 255 - opening
    opening = cv2.dilate(opening, None, iterations=1)
    contour_mask = 255 - opening
    opening[circle_mask == 0] = 0

    minLineLength = 100

    lines = cv2.HoughLinesP(image=opening, rho=1, theta=numpy.pi / 180, threshold=minLineLength, lines=numpy.array([]),
                            minLineLength=minLineLength, maxLineGap=12)
    grad = numpy.zeros((len(lines), 1))
    counter = 0
    for line in lines:
        x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
        theta = math.atan(float(y2 - y1) / (x2 - x1)) * 180 / math.pi
        grad[i] = theta
        counter += 1
        cv2.line(contour_mask, (x1, y1), (x2, y2), 0, 1, cv2.LINE_AA)
    hist, bin_edges = numpy.histogram(grad, density=False)
    ind = numpy.argmax(hist)
    best_grad = round((bin_edges[ind] + bin_edges[ind + 1]) / 2, 2)
    ind = numpy.where(numpy.abs(grad - best_grad) < 10)
    good_grads = grad[ind]
    best_grad = numpy.mean(good_grads)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), best_grad, 1)
    contour_mask = cv2.warpAffine(contour_mask, M, (w, h))
    (contours, _) = cv2.findContours(contour_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour_mask = cv2.cvtColor(contour_mask, cv2.COLOR_GRAY2BGR)
    areas = []
    border = 0
    r = []

    # tile real world dimension
    real_w, real_h = 0.25, 0.12

    for contour in contours:
        rect = cv2.boundingRect(contour)

        if rect[0] > border and rect[0] + rect[2] < w - border and rect[1] > border and rect[3] + rect[1] < h - border:
            area = int(rect[3] * rect[2])
            # print(area)
            ar = float(rect[2]) / rect[3]
            real_ar = real_w / real_h
            if area > 1000 and area < 120000 and abs(ar / real_ar - 1) < 0.3:
                cv2.rectangle(contour_mask, (rect[0], rect[1]), (rect[2] + rect[0], rect[3] + rect[1]), (0, 255, 0), 2)
                areas.append(area)
                r.append(rect)
    areas = numpy.asarray(areas)
    hist, bin_edges = numpy.histogram(areas, bins='fd', density=False)
    ind = numpy.argmax(hist)
    best_area = round((bin_edges[ind] + bin_edges[ind + 1]) / 2, 2)
    ind = numpy.where(numpy.abs(areas - best_area) < 0.1 * best_area)
    if len(ind) > 5:
        good_areas = areas[ind]
        best_area = numpy.mean(good_areas)

    # initialize depth
    depth = 0

    if best_area < 10:
        depth = 0
    else:
        # fov of camera
        fov_w, fov_h = 48 * math.pi / 180, 36 * math.pi / 180
        px_W, px_H = 640, 480

        # pixel tile size
        px_w = math.sqrt(area / (real_w * real_h)) * real_w
        px_h = math.sqrt(area / (real_w * real_h)) * real_h
        # print(px_w, px_h)

        # camera fov in meters
        W = px_W * real_w / px_w
        H = px_H * real_h / px_h

        # predict depth
        d_w = W / (2 * math.tan(fov_w / 2))
        d_h = H / (2 * math.tan(fov_h / 2))
        depth = (d_w + d_h) / 2

    # pitch angle and roll angle from imu
    pitch = 0
    roll = 0
    depth = depth * math.cos(pitch) * math.cos(roll)
    return depth
