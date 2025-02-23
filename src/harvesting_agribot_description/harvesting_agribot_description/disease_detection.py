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

object_detector=True
bridge=CvBridge()
class disease_detection(Node):

    def __init__(self):
        super().__init__("camera_subscriber")
        self.disease_status = self.create_publisher(String, '/harvesting_bot/disease_detected', 10)
        self.goal_position = self.create_subscription(String, '/harvesting_bot/goal_status', self.goal_status,10)
        self.declare_parameter('virtual_world',True)
        self.virtual_world = self.get_parameter('virtual_world').value
        self.disease_detected=False
        self.goal_reached = False
        self.time_out_duration = 5.0
        self.timer = None
        self.camera_subscriber = self.create_subscription(Image, '/harvesting_bot/harvesting_bot_camera/color/image_raw', self.object_detection,10)

    def goal_status(self, msg:String):
        if msg.data == 'GOAL REACHED':
            print("Disease Detection Model is running for ",self.time_out_duration," seconds")
            self.goal_reached = True
            self.get_logger().info("Goal reached!")
            self.timer=self.create_timer(self.time_out_duration,self.stop_timer)

    def object_detection(self, msg: Image):
        if self.goal_reached == True:
            if self.virtual_world==False:
                print("Disease_detection is going to take place in real world")
                model = YOLO("/home/don/harvesting_robot/kbot_mk1/src/kbot/yolo_models/yolov8m.pt")
                if object_detector==True:
                    self.disease_detected=False
                    img = bridge.imgmsg_to_cv2(msg)
                    results=model.predict(source=img, conf=0.75)
                    global point_y,point_x,depth_data_collector,plant_counter
                    point_x,point_y =[],[]
                    for result in results:
                        boxes=result.boxes
                        label=torch.Tensor.tolist(boxes.cls)
                        boxy=torch.Tensor.tolist(boxes.xywh)
                        for l in range (len(label)):
                            if label[l] == 1.0:
                                self.disease_detected=True
                                self.stop_timer()
                    cv2.imshow("Image",img)
                    cv2.waitKey(1)
                    object_detector=False
            else:
                #For simulation, random predictions are created for the virtual fertilizer spraying agribot
                self.disease_detected=random.choice('TF')
                

    def stop_timer(self):
        print("Disease detection model is stopping")
        self.timer.destroy()
        disease=String()
        print("Disease detected :",self.disease_detected)
        disease.data=self.disease_detected
        self.disease_status.publish(disease)
        self.goal_reached=False

def main(args=None):
    rclpy.init(args=args)
    node = disease_detection()
    cv2.destroyAllWindows() 
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
