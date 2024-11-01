import os

import cv2
import numpy as np


def xyxy2xywh(bboxes):  # bboxes is a n,4 numpy array in format x1,y1,x2,y2
    if len(bboxes) == 0:
        return bboxes
    bboxes[:, 2] = bboxes[:, 2] - bboxes[:, 0]  # w = x2 -x1
    bboxes[:, 3] = bboxes[:, 3] - bboxes[:, 1]  # h = y2 - y1
    bboxes[:, 0] = bboxes[:, 0] + bboxes[:, 2] / 2  # x = x1 + w/2
    bboxes[:, 1] = bboxes[:, 1] + bboxes[:, 3] / 2  # y = y1 + h/2
    return bboxes


def xywh2xyxy(bboxes):  # bboxes is a n,4 numpy array in format xc,yc,w,h
    if len(bboxes) == 0:
        return bboxes
    bboxes[:, 0] = bboxes[:, 0] - bboxes[:, 2] / 2  # x1 = x - w/2
    bboxes[:, 1] = bboxes[:, 1] - bboxes[:, 3] / 2  # y1 = y - h/2
    bboxes[:, 2] = bboxes[:, 0] + bboxes[:, 2]  # x2 = x1 + w
    bboxes[:, 3] = bboxes[:, 1] + bboxes[:, 3]  # y2 = y1 + h
    return bboxes


def scale_boxes(boxes, h, w):
    if len(boxes) == 0:
        return boxes
    boxes[:, 3] *= h
    boxes[:, 2] *= w
    boxes[:, 1] *= h
    boxes[:, 0] *= w
    return boxes


def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    if x2 < x1 or y2 < y1:
        return 0.0
    intersection = (x2 - x1) * (y2 - y1)
    area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area_box2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    iou = intersection / float(area_box1 + area_box2 - intersection)
    return iou
