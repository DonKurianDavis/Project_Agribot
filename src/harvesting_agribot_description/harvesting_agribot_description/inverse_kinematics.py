from moveit_msgs.srv import GetPositionIK
from moveit_msgs.msg import RobotState, Constraints, PositionIKRequest
from sensor_msgs.msg import JointState
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
from std_msgs.msg import Header
from builtin_interfaces.msg import Time
import rclpy
import ast
from rclpy.node import Node
import serial
import math
import numpy as np

# arduino_data = serial.Serial("/dev/ttyACM0",baudrate=115200, timeout=3.0)
class inverse_kinematics(Node):
    def __init__(self):
        super().__init__('ik_client')
        self.client = self.create_client(GetPositionIK, '/compute_ik')

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        ik_request = PositionIKRequest()
        ik_request.group_name = 'arm'
        ik_request.robot_state = RobotState(
            joint_state=JointState(
                header=Header(stamp=Time(sec=0, nanosec=0), frame_id=''),
                name=[], position=[], velocity=[], effort=[]
            )
        )
        v1=[0,0,0.15]
        v2=[0.21500000715255735, 0.0312040131444932, 0.21668259292840963]
        
        q=[1.0, 0.0, 0.0, 0.0]
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
        print(q)
        ik_request.constraints = Constraints()
        ik_request.avoid_collisions = True
        ik_request.ik_link_name = 'link_5'
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
        
        # Call the service asynchronously
        self.future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, self.future)
        
        response = self.future.result()
        cmd=""
        if response.error_code.val == 1:  # SUCCESS
            
            joint_names = response.solution.joint_state.name
            joint_positions = response.solution.joint_state.position
            i = 0
            for name, position in zip(joint_names, joint_positions):
                if i!=5:
                    position=position*180/3.1415
                    print(f"Joint {name} has position {position}")
                    cmd=cmd+str(int(position))+","
                    i+=1
            cmd=cmd+"\r"
            print(cmd)
            # arduino_data.write(cmd.encode())
        else:
            print(f"IK computation failed with error code {response.error_code.val}")
            
def main():
    rclpy.init(args=None)
    ik_client = inverse_kinematics()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
