#!/usr/bin/env python3
import ast
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
import rclpy
import time
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from std_msgs.msg import String

class fertilizer_goal_navigator(Node):
    def __init__(self):
        super().__init__('fertilizer_goal_navigator')
        self.goal_publisher = self.create_subscription(String, '/fertilizer_bot/goal_status',self.new_goal_position, 10)
        self.goal_location = self.create_publisher(PoseStamped,"/fertilizer_bot/goal_location",10)
        self.declare_parameter('virtual_world',True)
        self.get_logger().info("Sending Goal from Main Controller to Slave Systems")
        self.virtual_world = self.get_parameter('virtual_world').value
        time.sleep(2)
        if (self.virtual_world==True):
            with open("landmarks/disease_detected_plants_for_virtual_world.txt","r") as data:
                str_goal_points = data.read()
                goal_points_list = ast.literal_eval(str_goal_points)
                new_goal_point = [0.0, 3.25, 0.0, 0.0, 0.0, -0.707, 0.707]
                goal_points_list.append(new_goal_point)
        else:
            with open("landmarks/disease_detected_plants_for_real_world.txt","r") as data:
                str_goal_points = data.read()
                goal_points_list = ast.literal_eval(str_goal_points)
        
        for point in goal_points_list:
            self.goal_pose = PoseStamped()
            self.goal_pose.header.frame_id = 'map'
            self.goal_pose.header.stamp = self.get_clock().now().to_msg()
            self.goal_pose.pose.position.x = float(point[0])
            self.goal_pose.pose.position.y = float(point[1])
            self.goal_pose.pose.position.z = float(point[2])
            self.goal_pose.pose.orientation.x = float(point[3])
            self.goal_pose.pose.orientation.y = float(point[4])
            self.goal_pose.pose.orientation.z = float(point[5])
            self.goal_pose.pose.orientation.w = float(point[6])
            self.next_goal_position=False
            self.goal_location.publish(self.goal_pose)
            future = rclpy.task.Future()  # Create a Future object
        
            while not self.next_goal_position and rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.5)  # Wait for next_goal_position to become True
            future.set_result(True)  # Mark future as completed

    def new_goal_position(self, msg):
        time.sleep(10)
        self.get_logger().info(f"Received new goal position: {msg.data}")
        self.next_goal_position = True    
            

    
        
def main(args=None):
    rclpy.init(args=args)
    navigator = fertilizer_goal_navigator()
    rclpy.spin_once(navigator)
    navigator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

