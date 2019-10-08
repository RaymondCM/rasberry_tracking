#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import cv2
import numpy as np

class LabelColours:
    def __init__(self, colour_list=None):
        if colour_list is None:
            colour_list = [[230, 25, 75], [60, 180, 75], [255, 225, 25], [0, 130, 200], [245, 130, 48], [145, 30, 180],
                           [70, 240, 240], [240, 50, 230], [210, 245, 60], [250, 190, 190], [0, 128, 128],
                           [230, 190, 255], [170, 110, 40], [255, 250, 200], [128, 0, 0], [170, 255, 195],
                           [128, 128, 0], [255, 215, 180], [0, 0, 128], [128, 128, 128], [255, 255, 255], [0, 0, 0]]
        self.colours = colour_list

    def __getitem__(self, item):
        if item < 0:
            item *= -1
        if item >= len(self.colours):
            item = item % len(self.colours)
        return self.colours[item]


def draw_detection_msg_on_image(image, detection_msg, font=cv2.FONT_HERSHEY_SIMPLEX,
                                    font_scale=0.5, font_colour=(255, 255, 255), line_type=8, encoding="rgb8"):
    label_colours = LabelColours()
    if "rgb" not in encoding:
        label_colours.colours = [list(reversed(l)) for l in label_colours.colours]

    classes = detection_msg.class_labels
    bounding_box_msgs = detection_msg.bounding_boxes
    segmentation_lbl_msgs = detection_msg.instances if detection_msg.instances else None

    if segmentation_lbl_msgs is not None and len(bounding_box_msgs) != len(segmentation_lbl_msgs):
        raise ValueError("Incorrect annotation data passed (different lengths)")

    n_detections = len(bounding_box_msgs)
    for detection_id in range(n_detections):
        bounding_box = bounding_box_msgs[detection_id]
        mask = None if segmentation_lbl_msgs is None else (segmentation_lbl_msgs[detection_id].x,
                                                           segmentation_lbl_msgs[detection_id].y)

        pt1 = (int(bounding_box.x1), int(bounding_box.y1))
        pt2 = (int(bounding_box.x2), int(bounding_box.y2))
        class_colour = label_colours[bounding_box.class_id]
        class_colour_f = [float(f) / 2 for f in class_colour]
        cv2.rectangle(image, pt1, pt2, color=class_colour)

        if mask is not None:
            image[mask] = (image[mask] * 0.5) + class_colour_f

        if classes is not None:
            padding = 10
            class_name = "{} {}%".format(classes[bounding_box.class_id], int(bounding_box.score * 100))
            text_width, text_height = cv2.getTextSize(class_name, font, font_scale, line_type)[0]
            pt3 = (pt1[0], pt1[1])
            pt4 = (pt1[0] + text_width + (padding // 2), pt1[1] - text_height - padding)
            cv2.rectangle(image, pt3, pt4, color=class_colour, thickness=-1)
            pt5 = (pt1[0] + (padding // 2), pt1[1] - (text_height // 2))
            cv2.putText(image, class_name, pt5, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_colour, lineType=line_type)
    return image