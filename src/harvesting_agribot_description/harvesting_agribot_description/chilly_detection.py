#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import rclpy.time
from moveit_msgs.srv import GetPositionIK
from moveit_msgs.msg import RobotState, Constraints, PositionIKRequest
from sensor_msgs.msg import JointState,Image,PointCloud2
from cv_bridge import CvBridge
from ultralytics import YOLO
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Twist, PointStamped
import sensor_msgs_py.point_cloud2 as pc2
from tf2_ros import TransformListener, Buffer
import tf2_geometry_msgs
import cv2
import torch
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
from std_msgs.msg import Header
from builtin_interfaces.msg import Time
from std_msgs.msg import String,Bool
import serial
import numpy as np
import time

chilly_counter=0
depth_data_collector=False
object_detector=True
bridge=CvBridge()
model = YOLO("models/chilly_detection.pt")
plant_coordinates=[]
plant_coordinate=[]
goal_poses=[]
global_chilly_coordinates=[]

class chilly_detection(Node):

    def __init__(self):
        super().__init__("harvesting_bot_camera_subscriber")
        self.client = self.create_client(GetPositionIK, '/compute_ik')
        self.camera_subscriber = self.create_subscription(Image,'/harvesting_bot/harvesting_bot_camera/color/image_raw',self.object_detection,10)
        self.declare_parameter('virtual_world',True)
        self.virtual_world = self.get_parameter('virtual_world').value
        self.depthcamera_subscriber = self.create_subscription(PointCloud2,'/harvesting_bot/harvesting_bot_camera/depth/color/points',self.distance_calculator,10)
        self.goal_position = self.create_subscription(String, '/harvesting_bot/goal_status', self.goal_status,10)
        self.marker_publisher = self.create_publisher(Marker, '/visualization_marker', 10)
        self.chilly_timeout = self.create_publisher(Bool, '/harvesting_bot/chilly_timer', 10)
        self._tf_buffer = Buffer()
        self.listener = TransformListener(self._tf_buffer, self)
        self.goal_reached = False
        self.processing_in_progress = False
        self.time_out_duration = 15.0
        self.timer = None
        print("Detection System has been activated")
        if self.virtual_world == False:
            global arduino_data
            arduino_data = serial.Serial("/dev/ttyACM1",baudrate=115200, timeout=3.0)
            

    def goal_status(self, msg:String):
        if msg.data == 'GOAL REACHED':
            time.sleep(self.time_out_duration)
            self.goal_reached = True
            self.get_logger().info("Goal reached!")
            self.timer=self.create_timer(self.time_out_duration,self.object_detection_timer)
            print("Timer have started")
        else:
            timeout = Bool()
            timeout.data = True
            self.chilly_timeout.publish(timeout)
    
    def stop_timer(self):
        print("Chilly Timer has stopped as it was able to perform inverse kinematics")
        self.timer.cancel()
        
    def reset_timer(self):
        print("Chilly Timer has resetted as it was able to perform inverse kinematics")
        self.timer=self.create_timer(self.time_out_duration,self.object_detection_timer)


    def object_detection_timer(self):
        self.timer.destroy()
        print("Chilly Timer has ended")
        self.processing_in_progress = False
        self.goal_reached = False
        timeout = Bool()
        timeout.data = True
        self.chilly_timeout.publish(timeout)

    def object_detection(self, msg: Image):
        if self.goal_reached == True and self.processing_in_progress == False and self.virtual_world==False:
            self.destroy_subscription(self.camera_subscriber)
            img = bridge.imgmsg_to_cv2(img_msg=msg,desired_encoding='bgr8')
            # img = cv2.resize(c_img,(848,480))
            results=model.predict(source=img,show=False,conf=0.2,imgsz=(640,480))
            global bounding_box,depth_data_collector,chilly_counter
            bounding_box=[]
            for result in results:
                boxes=result.boxes
                label=torch.Tensor.tolist(boxes.cls)
                boxy=torch.Tensor.tolist(boxes.xyxy)
                chilly_counter=0
                for l in range (len(label)):
                    if label[l] == 0.0:
                        print("Object Detected")
                        chilly_counter+=1
                        print(boxy[l])
                        bounding_box.append(boxy[l])
                        depth_data_collector=True
                if chilly_counter==0:
                    depth_data_collector=False
                    # self.camera_subscriber = self.create_subscription(Image,'/harvesting_bot/harvesting_bot_camera/color/image_raw',self.object_detection,10)

    def distance_calculator(self, data: PointCloud2):
        if self.goal_reached==True and self.processing_in_progress == False and self.virtual_world==False:
            self.destroy_subscription(self.depthcamera_subscriber)
            if (depth_data_collector==True):
                self.processing_in_progress=True
                print("Point Cloud Calculator",chilly_counter)
                i,w=0,0
                valid_points_list = [[] for i in range(chilly_counter)] 
                for point in pc2.read_points(data, field_names=("x", "y", "z"),skip_nans=False):
                    if i<(data.width-1):
                        i+=1
                    else:
                        i=0
                        w+=1
                    for counter in range(chilly_counter):
                        if (bounding_box[counter][0]<= i <= bounding_box[counter][2] and bounding_box[counter][1]<= w <= bounding_box[counter][3]):
                            if not point[0]==point[1]==point[2]==0.0:
                                valid_points_list[counter].append(point)
                                # print(bounding_box[counter][0]," <= ",i," <= ",bounding_box[counter][2]," and", bounding_box[counter][1]," <=", w ," <= ",bounding_box[counter][3])
                                # print(point)
                for valid_points in valid_points_list:
                        if valid_points:
                                points_array = np.array(valid_points)
                                points_array = np.array([(p[0], p[1], p[2]) for p in valid_points], dtype=np.float32)
                                distances = np.linalg.norm(points_array, axis=1)

                                # Find the index of the closest point
                                closest_index = np.argmin(distances)

                                # Get the closest point
                                closest_point = points_array[closest_index]

                                print(f"Closest Point: {closest_point}")
                                point = min(valid_points, key=lambda p: (p[0]**2 + p[1]**2 + p[2]**2))
                                print(point)
                                camera_point = PointStamped()
                                camera_point.header.frame_id="harvesting_bot_camera_depth_optical_frame"
                                camera_point.point.x=float(point[0])
                                camera_point.point.y=float(point[1])
                                camera_point.point.z=float(point[2])
                                timeToLookUp = rclpy.time.Time() 
                                transform = self._tf_buffer.lookup_transform("braccio_base", "harvesting_bot_camera_depth_optical_frame", timeToLookUp, timeout=Duration(seconds=0.0))
                                base_point = tf2_geometry_msgs.do_transform_point(camera_point, transform)
                                goal_pose = PointStamped()
                                goal_pose.header.frame_id = 'braccio_base'
                                goal_pose.point.x = float(base_point.point.x)
                                goal_pose.point.y = float(base_point.point.y)
                                goal_pose.point.z = float(base_point.point.z)
                                print(goal_pose.point.x,",",goal_pose.point.y,",",goal_pose.point.z)
                                marker = Marker()
                                marker.header.frame_id = 'braccio_base'
                                marker.header.stamp = self.get_clock().now().to_msg()
                                marker.ns = "chilly_object"
                                marker.id = 0
                                marker.type = Marker.SPHERE  # Use a sphere to represent the point
                                marker.action = Marker.ADD

                                # Set the position of the marker to the transformed point
                                marker.pose.position.x = base_point.point.x
                                marker.pose.position.y = base_point.point.y
                                marker.pose.position.z = base_point.point.z
                                
                                # Set the marker scale (size)
                                marker.scale.x = 0.05  # radius of the sphere
                                marker.scale.y = 0.05
                                marker.scale.z = 0.05

                                # Set the color (red for visibility)
                                marker.color.r = 1.0
                                marker.color.g = 0.0
                                marker.color.b = 0.0
                                marker.color.a = 1.0  # Fully opaque

                                # Publish the Marker
                                self.marker_publisher.publish(marker)
                                print("Passing coordintes to Moveit Inverse Kinematics")
                                ik_request = PositionIKRequest()
                                ik_request.group_name = 'arm'
                                ik_request.robot_state = RobotState(
                                    joint_state=JointState(
                                        header=Header(stamp=Time(sec=0, nanosec=0), frame_id=''),
                                        name=["base_joint","shoulder_joint","elbow_joint","wrist_pitch_joint","wrist_roll_joint","gripper_joint","sub_gripper_joint"],
                                          position=[1.5707,0,0,2.8797,0,0,1.5707], velocity=[], effort=[]
                                    )
                                )
                                ik_request.constraints = Constraints()
                                ik_request.avoid_collisions = False
                                ik_request.ik_link_name = 'link_5'
                                v1=[0,0,round(goal_pose.point.z,2)]
                                v2=[round(goal_pose.point.x-0.05,2),round(goal_pose.point.y,2),round(goal_pose.point.z,2)]
                                q=[1.0, 0.0, 0.0, 0.0]
                                print(v2)
                                direction = np.array(v2) - np.array(v1)
                                direction_norm = direction / np.linalg.norm(direction)
                                reference_vector = np.array([0, 0, 1])
                                axis = np.cross(reference_vector, direction_norm)
                                angle = np.arccos(np.dot(reference_vector, direction_norm))
                                if np.linalg.norm(axis) < 1e-6:
                                    q=[1.0, 0.0, 0.0, 0.0]
                                else:
                                    axis = axis / np.linalg.norm(axis)
                                    q[0] = np.cos(angle / 2)
                                    q[1] = axis[0] * np.sin(angle / 2)
                                    q[2] = axis[1] * np.sin(angle / 2)
                                    q[3] = axis[2] * np.sin(angle / 2)
                                ik_request.pose_stamped = PoseStamped(
                                    header=Header(stamp=Time(sec=0, nanosec=0), frame_id='braccio_base'),
                                    pose=Pose(
                                        position=Point(x=v2[0], y=v2[1], z=v2[2]),
                                        orientation=Quaternion(x=q[1], y=q[2], z=q[3], w=q[0])

                                    )
                                )
                                
                                # Create the GetPositionIK.Request object and set the ik_request
                                request = GetPositionIK.Request()
                                request.ik_request = ik_request
                                print("Performing Inverse Kinematics for point",v2)
                                # Call the service asynchronously
                                self.future = self.client.call_async(request)
                                self.future.add_done_callback(self.process_ik_response)
                                continue
                self.camera_subscriber = self.create_subscription(Image,'/harvesting_bot/harvesting_bot_camera/color/image_raw',self.object_detection,10)
                self.depthcamera_subscriber = self.create_subscription(PointCloud2,'/harvesting_bot/harvesting_bot_camera/depth/color/points',self.distance_calculator,10)
         

    def process_ik_response(self, future):
        response = future.result()
        cmd=""
        if response.error_code.val == 1:  # SUCCESS
            joint_names = response.solution.joint_state.name
            joint_positions = response.solution.joint_state.position
            i=0
            for name, position in zip(joint_names, joint_positions):
                i+=1
                position=position*180/3.1415
                print(f"Joint {name} has position {position}")
                if i<5:
                    cmd=cmd+","+str(int(position))
            cmd=cmd[1::]+",0,\r"
            print(cmd)
            self.stop_timer()
            arduino_data.write(cmd.encode())
            time.sleep(25)
            self.reset_timer()
            self.camera_subscriber = self.create_subscription(Image,'/harvesting_bot/harvesting_bot_camera/color/image_raw',self.object_detection,10)
            self.depthcamera_subscriber = self.create_subscription(PointCloud2,'/harvesting_bot/harvesting_bot_camera/depth/color/points',self.distance_calculator,10)
        else:
            print(f"IK computation failed with error code {response.error_code.val}")
        # self.camera_subscriber = self.create_subscription(Image,'/harvesting_bot/harvesting_bot_camera/color/image_raw',self.object_detection,10)
        # self.depthcamera_subscriber = self.create_subscription(PointCloud2,'/harvesting_bot/harvesting_bot_camera/depth/color/points',self.distance_calculator,10)
        self.processing_in_progress=False
    

def main(args=None):
    rclpy.init(args=None)
    node = chilly_detection()
    try:
        rclpy.spin(node)
    except SystemExit:
        print("Quitting")
    cv2.destroyAllWindows() 
    rclpy.shutdown()

if __name__ == '__main__':
    main()
