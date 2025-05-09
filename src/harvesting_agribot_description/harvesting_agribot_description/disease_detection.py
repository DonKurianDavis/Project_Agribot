#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import rclpy.time
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2
from std_msgs.msg import String
import torch
import serial
import time
import random

bridge=CvBridge()
model = YOLO("models/chilly_disease_detection.pt")
class disease_detection(Node):

    def __init__(self):
        super().__init__("harvesting_bot_disease_detection_node")
        self.disease_status = self.create_publisher(String, '/harvesting_bot/disease_detected', 10)
        self.goal_position = self.create_subscription(String, '/harvesting_bot/goal_status', self.goal_status,10)
        self.declare_parameter('virtual_world',True)
        self.virtual_world = self.get_parameter('virtual_world').value
        self.disease_detected="F"
        self.goal_reached = True
        self.object_detector=True
        self.time_out_duration = 5.0
        self.timer = None
        print("Disease Detection System has been activated")

    def goal_status(self, msg:String):
        if msg.data == 'GOAL REACHED':
            print("Disease Detection Model is running for ",self.time_out_duration," seconds")
            self.goal_reached = True
            self.get_logger().info("Goal reached!")
            self.timer=self.create_timer(self.time_out_duration,self.stop_timer)
            self.camera_subscriber = self.create_subscription(Image, '/harvesting_bot/harvesting_bot_camera/color/image_raw', self.object_detection,10)


    def object_detection(self, msg: Image):
        # self.destroy_subscription(self.camera_subscriber)
        if self.goal_reached == True:
            if self.virtual_world==False:
                print("Disease_detection is going to take place in real world")
                model = YOLO("models/chilly_disease_detection.pt")
                if self.object_detector==True:
                    self.disease_detected="F"
                    img = bridge.imgmsg_to_cv2(msg,desired_encoding='bgr8')
                    results=model.predict(source=img,conf=0.5,show=False)
                    global point_y,point_x
                    point_x,point_y =[],[]
                    for result in results:
                        boxes=result.boxes
                        label=torch.Tensor.tolist(boxes.cls)
                        boxy=torch.Tensor.tolist(boxes.xywh)
                        for l in range (len(label)):
                            if label[l] != 0.0:
                                self.disease_detected="T"
                                self.stop_timer()
                    # cv2.imshow("Image",img)
                    # cv2.waitKey(1)
                    self.object_detector=False
            else:
                #For simulation, random predictions are created for the virtual fertilizer spraying agribot
                self.disease_detected=random.choice('TF')
                

    def stop_timer(self):
        self.timer.destroy()
        self.destroy_subscription(self.camera_subscriber)
        disease=String()
        print("Disease detected :",self.disease_detected)
        disease.data=self.disease_detected
        self.disease_status.publish(disease)
        self.goal_reached=False
        self.get_logger().info("Disease Detection Model has ended")


def main(args=None):
    rclpy.init(args=args)
    node = disease_detection()
    cv2.destroyAllWindows() 
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
