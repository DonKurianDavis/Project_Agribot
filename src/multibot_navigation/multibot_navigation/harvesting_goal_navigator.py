#!/usr/bin/env python3
import ast
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
import rclpy
import time
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from rclpy.node import Node
from action_msgs.msg import GoalStatus
import rclpy.wait_for_message
from std_msgs.msg import String,Int16,Bool

class harvesting_goal_navigator(Node):
    def __init__(self):
        super().__init__('harvesting_goal_navigator')
        self.goal_location = self.create_publisher(PoseStamped,"/harvesting_bot/goal_location",10)
        self.disease_detection = self.create_subscription(String, '/harvesting_bot/disease_detected',self.disease_plant_coordinates,10)
        self.diseased_plants = self.create_publisher(Int16, '/harvesting_bot/diseased_plants',10)
        self.next_goal = self.create_subscription(Bool, '/harvesting_bot/chilly_timer',self.new_goal_position,10)
        # Initialize ActionClient
        self.get_logger().info("Sending Goal from Main Controller to Slave Systems")
        self.declare_parameter('virtual_world',True)
        self.virtual_world = self.get_parameter('virtual_world').value
        self.disease_pose=[]
        time.sleep(2)
        self.disease_points=self.plant_points=0
        self.prev_pos=-1
        self.goal_poses=[]
        self.next_goal_position = False
        # Wait for the action server to be available
        if (self.virtual_world==True):
            with open("landmarks/plant_coordinates_for_virtual_world.txt","r") as data:
                str_goal_points = data.read()
                goal_points_list = ast.literal_eval(str_goal_points)
                new_goal_point = [-1.0, 3.25, 0.0, 0.0, 0.0, -0.707, 0.707]
                goal_points_list.append(new_goal_point)
        else:
            with open("landmarks/plant_coordinates_for_real_world.txt","r") as data:
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
            self.goal_location.publish(self.goal_pose)
            self.next_goal_position=False
            future = rclpy.task.Future()
            while not self.next_goal_position and rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.5)  # Wait for next_goal_position to become True
            future.set_result(True)

    def new_goal_position(self, msg):
        self.get_logger().info(f"Received new goal position: {msg.data}")
        self.next_goal_position = True    
    
    def disease_plant_coordinates(self, msg: String):
        msi=Int16()
        if(msg.data=="T"):
            if self.prev_pos!=(self.plant_points//4):
                self.prev_pos=self.plant_points//4
                self.disease_points+=1
                msi.data=self.disease_points
                self.diseased_plants.publish(msi)
            print("Coordinates of disease affected plants are stored in database")
            self.disease_pose.append([self.goal_pose.pose.position.x,self.goal_pose.pose.position.y,0.0,0.0,0.0,self.goal_pose.pose.orientation.y,self.goal_pose.pose.orientation.z])
            if (self.virtual_world==True):
                with open("landmarks/disease_detected_plants_for_virtual_world.txt","w") as output:
                    output.write(str(self.disease_pose))
            else:
                with open("landmarks/disease_detected_plants_for_real_world.txt","w") as output:
                    output.write(str(self.disease_pose))
            with open("gui/no_of_disease_affected_and_chilly_harvested.txt","w") as output:
                    output.write(str(self.disease_points))
        self.plant_points+=1

    
        
def main(args=None):
    rclpy.init(args=args)
    navigator = harvesting_goal_navigator()
    executor = MultiThreadedExecutor()
    executor.add_node(navigator)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:    navigator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

