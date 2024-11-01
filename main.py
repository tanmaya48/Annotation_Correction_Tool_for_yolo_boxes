import os
from dataclasses import dataclass
import cv2
import numpy as np
import argparse
import constants as C
import yolo_io
from get_imagesize import get_imagesize 


def draw_boxes(image,image_data):
    target_image = image.copy()
    for data in image_data:
        classes,boxes,tag_colors,default_color = data
        for idx,box in enumerate(boxes):
            x1,y1,x2,y2 = box
            cv2.rectangle(target_image,(x1,y1),(x2,y2),tag_colors[idx],3)
            cv2.putText(target_image, str(classes[idx]), (x1,y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, tag_colors[idx], 2, cv2.LINE_AA)
            cv2.putText(target_image, str(classes[idx]), (x1,y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 1, cv2.LINE_AA)
    return target_image


Mouse_x = 0
Mouse_y = 0
Mouse_event = False
def mouse_callback(event, x, y, flags, param):
    global Mouse_x,Mouse_y,Mouse_event
    if event == cv2.EVENT_LBUTTONDOWN:
        Mouse_event = True
        Mouse_x = x
        Mouse_y = y


def assign_tags(x,y,image_data):
    box_found = False
    for data in image_data:
        if box_found:
            break
        classes,boxes,tag_colors,default_color = data
        tag_id = -1
        for i,box in enumerate(boxes):
            x1,y1,x2,y2 = box
            if x1 < x < x2 and y1 < y < y2:
                tag_id = i
                break
        if tag_id == -1: # if nothing is clicked on, unselect the current selection and return 
            for i in range(len(tag_colors)):
                if tag_colors[i] == C.white:
                    tag_colors[i] = default_color
            continue
        elif tag_colors[tag_id] == default_color: # assign new selection
            tag_colors[tag_id] = C.white 
        elif tag_colors[tag_id] in C.color_order[:-1]: # if box is selected or tagged
            new_color = C.color_order[C.color_order.index(tag_colors[tag_id]) + 1] # change tag/selection to the next
            tag_colors[tag_id] = new_color
        else:
            tag_colors[tag_id] = default_color
        box_found = True
    return


def update_state(key,program_state):
    exit_image = False
    if key == ord('q'):
        program_state.is_running = False
        exit_image = True
    if key == ord('n'):
        program_state.image_id+=1
        exit_image = True
    if key == ord('p'):
        program_state.image_id-=1
        exit_image = True
    if key == ord('c'):
        program_state.command_mode = True
        exit_image = True
    return exit_image


def mark_image(program_state,image,image_data):
    image_with_boxes = draw_boxes(image,image_data)
    global Mouse_event,Mouse_x,Mouse_y
    while True:
        cv2.imshow("NAT",image_with_boxes)
        cv2.setMouseCallback('NAT', mouse_callback)
        key = cv2.waitKey(20)
        exit_image = update_state(key,program_state)
        if exit_image:
            break
        if Mouse_event:
            Mouse_event = False
            assign_tags(Mouse_x,Mouse_y,image_data)
            image_with_boxes = draw_boxes(image,image_data)
    return image_data 


def process_command(existing_data,image_data,program_state):
    command = input("command mode >> ")
    words = command.split(' ')
    if words[0] == 'exit':
        return
    elif words[0] == 'export':
        program_state.export_set = int(words[1])
        return
    elif words[0] == 'is':
        label = int(words[1])
        print(f'changing seletions label to {label}')
        for data in image_data:
            classes,boxes,tag_colors,default_color = data
            for i in range(len(boxes)):
                if tag_colors[i] == C.white:
                    classes[i] = label
    elif words[0] == 'untag':
        color = eval(f'C.{words[1]}')
        for key,key_image_data in existing_data.items():
            for data in key_image_data:
                classes,boxes,tag_colors,default_color = data
                for i in range(len(boxes)):
                    if tag_colors[i] == color:
                        tag_colors[i] = default_color
    elif words[0] == 'delete':
        color = eval(f'C.{words[1]}')
        for key,key_image_data in existing_data.items():
            for data in key_image_data:
                classes,boxes,tag_colors,default_color = data
                remove_ids = []
                for i in range(len(boxes)):
                    if tag_colors[i] == color:
                        remove_ids.append(i)
                remove_ids.reverse()
                for idx in remove_ids:
                    boxes.pop(idx)
                    classes.pop(idx)
                    tag_colors.pop(idx)
    elif eval(f'C.{words[0]}') in C.color_order:
        color = eval(f'C.{words[0]}')
        if words[1] == 'is':
            label = int(words[2])
            print(f'changing tag {words[0]} label to {label}')
            for key,key_image_data in existing_data.items():
                for data in key_image_data:
                    classes,boxes,tag_colors,default_color = data
                    for i in range(len(boxes)):
                        if tag_colors[i] == color:
                            classes[i] = label
        elif words[1] == 'to':
            set_id = int(words[2])
            for key,key_image_data in existing_data.items():
                new_boxes = []
                new_classes = []
                for data in key_image_data:
                    classes,boxes,tag_colors,default_color = data
                    remove_ids = []
                    for i in range(len(boxes)):
                        if tag_colors[i] == color:
                            remove_ids.append(i)
                    remove_ids.reverse()
                    for idx in remove_ids:
                        new_boxes.append(boxes.pop(idx))
                        new_classes.append(classes.pop(idx))
                        tag_colors.pop(idx)
                #
                classes,boxes,tag_colors,default_color = key_image_data[set_id]
                for i in range(len(new_boxes)):
                    boxes.append(new_boxes[i])
                    classes.append(new_classes[i])
                    tag_colors.append(color)


    
@dataclass
class Program_state:
    image_id: int
    is_running: bool
    command_mode: bool
    export_set: int




if __name__ == '__main__':
    images_dir = ''
    labels_dir = ''
    export_dir = 'export'
    if not os.path.exists(export_dir):
        os.mkdir(export_dir)
    images = os.listdir(images_dir)
    program_state = Program_state(0,True,False,-1)
    existing_data = {}
    while program_state.is_running:
        image_name = images[program_state.image_id]
        image_path = os.path.join(images_dir,image_name)
        image = cv2.imread(image_path)
        #
        if image_name in existing_data.keys():
            image_data = existing_data[image_name]
        else:
            label_path = os.path.join(labels_dir,os.path.splitext(image_name)[0]+'.txt')
            h,w,_ = image.shape
            classes, boxes = yolo_io.get_data_from_yolo_label_file(label_path, h, w)
            boxes = [box for box in boxes]
            tag_colors = [C.GT_COLOR for box in boxes]
            image_data= [[classes,boxes,tag_colors,C.GT_COLOR],[[1],[[20,20,100,100]],[C.PRED_COLOR],C.PRED_COLOR]] # dummy data for second set
        #
        mark_image(program_state,image,image_data)
        existing_data[image_name] = image_data 
        if program_state.command_mode:
            program_state.command_mode = False
            process_command(existing_data,image_data,program_state)
        #
        if program_state.export_set != -1:
            for image_name,key_image_data in existing_data.items():
                data = key_image_data[program_state.export_set]
                classes,boxes,tag_colors,default_color = data
                im_width,im_height = get_imagesize(os.path.join(images_dir,image_name))
                label_name = os.path.splitext(image_name)[0] + '.txt'
                yolo_io.save_yolo_labels(os.path.join(export_dir,label_name),classes,np.array(boxes),im_height,im_width)
            program_state.export_set = -1
        #
        for data in image_data:
            classes,boxes,tag_colors,default_color = data
            for i in range(len(tag_colors)):
                if tag_colors[i] == C.white:
                    tag_colors[i] = default_color 

