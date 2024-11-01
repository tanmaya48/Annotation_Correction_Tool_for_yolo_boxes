import cv2
import numpy as np
from bbox_utils import scale_boxes, xywh2xyxy, xyxy2xywh


def read_yolo_label(label_path):
    with open(label_path, "r") as f:
        data = f.readlines()
    data = [line for line in data if len(line) > 2]
    classes = [int(line.split()[0]) for line in data]
    true_boxes = [[float(val) for val in line.split()[1:5]] for line in data]
    return classes, true_boxes


def get_data_from_yolo_label_file(label_path, h, w):
    if not os.path.exists(label_path):
        return [],[]
    classes, yolo_boxes = read_yolo_label(label_path)
    boxes = np.round(scale_boxes(xywh2xyxy(np.array(yolo_boxes)), h, w)).astype(int)
    return classes, boxes


def get_yolo_image_and_data(image_path, label_path):
    image = cv2.imread(image_path)
    h, w, _ = image.shape
    classes, boxes = get_data_from_yolo_label_file(label_path, h, w)
    return image, (classes, boxes)


def save_yolo_labels(label_path, classes, boxes, h, w):
    yolo_boxes = scale_boxes(xyxy2xywh(boxes.astype(np.float32)), 1 / h, 1 / w)
    with open(label_path, "w") as file:
        for class_id, box in zip(classes, yolo_boxes):
            x, y, w, h = box
            file.write(f"{class_id} {x} {y} {w} {h}\n")
