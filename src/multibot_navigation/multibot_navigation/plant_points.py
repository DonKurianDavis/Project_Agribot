#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

class plant_points(Node):
    goal_poses=[]
    def __init__(self):
        super().__init__("plant_point_placer")
        self.declare_parameter('virtual_world',True)
        self.goal_pose_subscriber  = self.create_subscription(PoseStamped,"harvesting_bot/goal_pose",self.plant_point_plotter,10)
        self.virtual_world = self.get_parameter('virtual_world').value
        
    
    def plant_point_plotter(self, msg: PoseStamped):
        if (self.virtual_world==True):
            self.goal_poses.append([msg.pose.position.x+0.65,msg.pose.position.y,0.0,0.0,0.0,1.0,0.0])
            self.goal_poses.append([msg.pose.position.x,msg.pose.position.y+0.65,0.0,0.0,0.0,-0.707,0.707])
            self.goal_poses.append([msg.pose.position.x-0.65,msg.pose.position.y,0.0, 0.0,0.0,0.0,1.0])
            self.goal_poses.append([msg.pose.position.x,msg.pose.position.y-0.65,0.0,0.0,0.0,0.707,0.707])
            print(self.goal_poses)
            with open("landmarks/plant_coordinates_for_virtual_world.txt","w") as output:
                output.write(str(self.goal_poses))
        else:
            self.goal_poses.append([msg.pose.position.x+0.4,msg.pose.position.y,0.0,0.0,0.0,1.0,0.0])
            self.goal_poses.append([msg.pose.position.x,msg.pose.position.y+0.4,0.0,0.0,0.0,-0.707,0.707])
            self.goal_poses.append([msg.pose.position.x-0.4,msg.pose.position.y,0.0, 0.0,0.0,0.0,1.0])
            self.goal_poses.append([msg.pose.position.x,msg.pose.position.y-0.4,0.0,0.0,0.0,0.707,0.707])
            print(self.goal_poses)
            with open("landmarks/plant_coordinates_for_real_world.txt","w") as output:
                output.write(str(self.goal_poses))

def main():
    rclpy.init(args=None)
    node = plant_points()
    rclpy.spin(node)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
