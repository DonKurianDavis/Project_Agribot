#! /usr/bin/env python3
 
import rclpy # Python client library for ROS 2
from rclpy.node import Node # Handles the creation of nodes
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from std_msgs.msg import Header  # Import the Header message
 
# Define constants
arm_joints = [ 'Revolute 11', 
               'Revolute 13']
 
class ExampleJointTrajectoryPublisherPy(Node):
        
    def __init__(self):
        
        super().__init__('example_joint_trajectory_publisher_py')    
  
        self.arm_pose_publisher = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 1)
        
        self.timer_period = 5.0  # seconds 5.0
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
 
        self.frame_id = "base_link"
        
        self.duration_sec = 2
        self.duration_nanosec = 0.5 * 1e9 # (seconds * 1e9)
 
        self.arm_positions = []
        self.arm_positions.append([1.570, 1.570, 2.094, 3.14, 3.14]) 
        self.arm_positions.append([1.570, 1.570, 1.570, 3.14, 3.14])
        self.arm_positions.append([1.570, 1.570, 2.094, 3.14, 3.14])
        self.arm_positions.append([1.570, 1.570, 1.570, 3.14, 3.14])

        self.arm_positions.append([2.094, 1.570, 1.570, 3.14, 3.14]) 
        self.arm_positions.append([1.047, 1.570, 1.570, 3.14, 3.14])
        self.arm_positions.append([2.094, 1.570, 1.570, 3.14, 3.14])
        self.arm_positions.append([1.047, 1.570, 1.570, 3.14, 3.14]) 
 
        self.index = 0
 
    def timer_callback(self):
        msg_arm = JointTrajectory()
        msg_arm.header = Header()  
        msg_arm.header.frame_id = self.frame_id  
        msg_arm.joint_names = arm_joints
 
        point_arm = JointTrajectoryPoint()
        point_arm.positions = self.arm_positions[self.index]
        point_arm.time_from_start = Duration(sec=int(self.duration_sec), nanosec=int(self.duration_nanosec))  # Time to next position
        msg_arm.points.append(point_arm)
        self.arm_pose_publisher.publish(msg_arm)
        
        if self.index == len(self.arm_positions) - 1:
            self.index = 0
        else:
            self.index = self.index + 1
     
def main(args=None):
   
    # Initialize the rclpy library
    rclpy.init(args=args)
    example_joint_trajectory_publisher_py = ExampleJointTrajectoryPublisherPy()
    rclpy.spin(example_joint_trajectory_publisher_py)
    example_joint_trajectory_publisher_py.destroy_node()
   
    rclpy.shutdown()
   
if __name__ == '__main__':
    main()