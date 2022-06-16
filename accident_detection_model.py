# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Building object tracking model
# Date Created: 17/06/2022

import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1" # uncomment to use CPU instead of GPU
from v_detect_track.object_tracking import object_tracker
import cv2
import time
from collections import deque
import numpy as np
import tensorflow as tf
graph = tf.get_default_graph()
from keras_retinanet import models
from keras_retinanet.utils.image import preprocess_image, resize_image

class fused_accident_detection:
    accident_frame = 0
    total_frames = 0 
    
    # vdet_model_path -> file path of trained Yolo, src=0 -> default: device camera
    # fskip=0 -> skip frame if required for better fps (default is 0)
    def __init__(self, vdet_model_path, src=0, fskip=0):
        tf.compat.v1.keras.backend.set_session(self.get_session())
        # Initiate vehicle tracker
        self.vot_model = object_tracker()
        self.font =cv2.FONT_HERSHEY_DUPLEX # configure font family to be used
        
        # Load tarined retinanet model for vehicle detection
        self.model = models.load_model(vdet_model_path, backbone_name='resnet50')
        
        # Initiate video source
        self.video_src = src
        self.video = cv2.VideoCapture(self.video_src)
        self.frame_skip = fskip
        
        # Setup frame estimation variables
        self.total_frames = 0
        self.total_fps = 0
        
        # Setup frame variables for tracking
        self.isInit_frame = True
        self.prev_frame_objs = []
        self.cur_frame_objs = []
    
    # Sets up Tensorflow/Keras backend 
    def get_session(self):
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True
        return tf.compat.v1.Session(config=config)
    
    # Processing each frame
    def proc_frame(self):
        start = time.time() # for frame calculation later
        
        # Frame skipping (based on fskip configured)
        for i in range(0, self.frame_skip):
            ava_frame, frame = self.video.read()
        
        # Frame to be processed
        ava_frame, frame = self.video.read()
        # If no more avaiable frame in the video
        if not ava_frame:
            self.video = cv2.VideoCapture(self.video_src)
            ava_frame, frame = self.video.read()
            
        # Padding the input video to fit training format
        rows = frame.shape[0]
        cols = frame.shape[1]
        if rows < cols:
            padding = int((cols - rows) / 2)
            frame = cv2.copyMakeBorder(frame, padding, padding, 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
        elif rows > cols:
            padding = int((rows - cols) / 2)
            frame = cv2.copyMakeBorder(frame, 0, 0, padding, padding, cv2.BORDER_CONSTANT, (0, 0, 0))
            
        # Detection on frame
        dup_frame = frame.copy() # duplicate frame for drawing on detection later
        # Preprocessing frame before inferencing
        frame = preprocess_image(frame)
        frame, scale = resize_image(frame, min_side=600)
        # Running actual inference on input frame
        with graph.as_default():
            boxes, scores, labels = self.model.predict_on_batch(np.expand_dims(frame, axis=0))
        boxes /= scale # Adjusting scale of bounding boxes since our frame is resized to 600p
        
        # Preparing for vehicle tracking
        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            # Class th
            if score < 0.60:
                break
            
            # Obtain midpoint
            x_midpt = int((box[2] + box[0]) / 2)
            y_midpt = int((box[3] + box[1]) / 2)
            
            # Track the detected vechicles
            # If is first frame
            if self.isInit_frame:
                self.prev_frame_objs.append([(x_midpt, y_midpt), self.vot_model.acq_init_idx(), 0, deque(), -1, 0])
            else:
                self.cur_frame_objs.append([(x_midpt, y_midpt), 0, 0, deque(), -1, 0])
        
         # Keep running vehicle tracking algorithm to track detections across frames
        if not self.isInit_frame:
            # Run when have object detected
            if (len(self.prev_frame_objs) != 0):
                self.cur_frame_objs = self.vot_model.arr_cur_objs(self.prev_frame_objs, self.cur_frame_objs)
                
        # FPS counter
        frm_time = time.time() - start
        self.total_fps += (1/frm_time)
        self.total_frames += 1
        fps = str(round((1/frm_time), 2))
        
        '''
        Tracking Object Storing Format:
            Index 0: Midpoint of object (tuple structure)
            Index 1: Object ID
            Index 2: Number of consecutive frames detected for
            Index 3: Midpoint of object over previous 5 consecutive frames (double-ended queue structure)
            Index 4: Points to the new obj according to old obj assigned (array structure) -> avoid conflict within tracked objs
            Index 5: Magnitude of object vectore in prev frame
        '''
        # Accident Detection (magnitude anomaly, classification) -> current frame
        isAcci_sus = False
        isAcci_conf = False
        for objs in self.cur_frame_objs:
            # Make sure the accident detection was made on objects that had been detected for over 5 frame
            if (objs[2] >= 5):
                ### Detect suspicious accident through magnitude of vector
                ## First Validation: changes in magnitude of vector
                # Acquring the vector of obj within 5 frames (centroid)
                vec = [objs[3][-1][0] - objs[3][0][0], objs[3][-1][1] - objs[3][0][1]] # x,y
                # Predict the obj next location
                next_loc_vec = (2 * vec[0] + objs[3][-1][0], 2 * vec[1] + objs[3][-1][1]) # pred -> 2*midpoint+max loc of 5 consecutive frame
                # Calculate magnitude of vector (euclidean dist)
                vec_mag = (vec[0]**2 + vec[1]**2)**(0.5)
                # Calculate for sudden change acceleration/deceleration of vehicle
                chg = abs(vec_mag - objs[5]) # index 5 -> magnitude in prev frame
                # Determine suspect accident (based on threshold defined -> if exceed threshold and vehicle is moving in prev frame)
                if (chg >= 11) and (objs[5] != 0.0):
                    isAcci_sus = True

                ## Second Validation: neural network accident classification (Resnet)
                # Pending here....
                
                ## Show detected vehicles and potential accidents
                if isAcci_sus:
                    cv2.circle(dup_frame, objs[0], 5, (0, 255, 255), 2) # radius 5, BGR yellow, thickness 2
                else:
                    cv2.circle(dup_frame, objs[0], 5, (0, 255, 0), 2) # radius 5, BGR green, thickness 2
                    
                ## Show predicting future loc of detected vehicles
                cv2.line(dup_frame, objs[3][-1], next_loc_vec, (255, 0, 0), 2) # BGR dark blue
            
        ## If accident confirm detected in the current frame
        if isAcci_conf:
            cv2.putText(dup_frame, "ACCIDENT DETECTED", (10, 10), self.font, 1, (0, 0, 255), 2, cv2.LINE_AA)
            
        cv2.putText(dup_frame, "FPS: {}".format(fps), (10, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        # Move next in object tracking
        if not self.isInit_frame:
            self.prev_frame_objs = self.cur_frame_objs.copy()
            self.cur_frame_objs = []
        
        # Reset initframe
        self.isInit_frame = False
        
        # Accumulate frame
        self.total_frames += 1
        if isAcci_conf:
            self.accident_frame += 1
        print((self.accident_frame / self.total_frames) * 100)
        
        return ava_frame, dup_frame, frm_time, isAcci_conf
    
    # End detection
    def __del__(self):
        self.video.release()
        
        
        
        
            
        