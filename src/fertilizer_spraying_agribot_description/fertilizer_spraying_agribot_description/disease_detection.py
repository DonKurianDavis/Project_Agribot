#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import rclpy.time
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2
import torch
import serial
from std_msgs.msg import String
import random,time

arduino_data = serial.Serial("/dev/ttyACM0",baudrate=115200, timeout=3.0)
object_detector=True
bridge=CvBridge()
model = YOLO("models/tomato_leaf_disease_detection.pt")
class disease_detection(Node):

    def __init__(self):
        super().__init__("camera_subscriber")
        self.goal_position = self.create_subscription(String, '/fertilizer_bot/goal_status', self.goal_status,10)
        self.camera_subscriber = self.create_subscription(Image,'/fertilizer_bot/fertilizer_bot_camera/color/image_raw',self.object_detection,10)
        self.declare_parameter('virtual_world',True)
        self.virtual_world = self.get_parameter('virtual_world').value
        self.time_out_duration = 5
        
    def goal_status(self, msg:String):
        if msg.data == 'GOAL REACHED':
            self.goal_reached = True
            self.get_logger().info("Goal reached!")
            self.timer=self.create_timer(self.time_out_duration,self.stop_timer)

    def object_detection(self, msg: Image):
        if self.goal_reached==True:
            if self.virtual_world==False:
                disease_detected=False
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
                            disease_detected=True
                    if disease_detected==True:
                        cmd="f"
                        arduino_data.write(cmd.encode())
                cv2.imshow("Image",img)
                cv2.waitKey(1)
            else:
                disease_detected=random.choice('TF')
                if disease_detected=='T':
                    cmd="f"
                    arduino_data.write(cmd.encode())
    def stop_timer(self):
        print("Disease detection model is stopping")
        self.timer.destroy()
        time.sleep(10)
        self.goal_reached=False

def main(args=None):
    rclpy.init(args=args)
    node = disease_detection()
    cv2.destroyAllWindows() 
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
