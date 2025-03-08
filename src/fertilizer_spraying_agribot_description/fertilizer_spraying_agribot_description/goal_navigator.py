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

class goal_navigator(Node):
  def __init__(self):
    super().__init__('goal_navigator')
    
    # Initialize ActionClient
    self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
    self.get_logger().info("Waiting for NavigateToPose action server...")
    
    # Wait for the action server to be available
    if not self.client.wait_for_server(timeout_sec=5.0):
        self.get_logger().error('NavigateToPose action server not available')
        return

    # Load goal poses from file
    with open("landmarks/coordinated_for_bot.txt", "r") as data:
        str_goal_points = data.read()
    goal_points_list = ast.literal_eval(str_goal_points)
    
    goal_poses = []
    for point in goal_points_list:
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = float(point[0])
        goal_pose.pose.position.y = float(point[1])
        goal_pose.pose.position.z = float(point[2])
        goal_pose.pose.orientation.x = float(point[3])
        goal_pose.pose.orientation.y = float(point[4])
        goal_pose.pose.orientation.z = float(point[5])
        goal_pose.pose.orientation.w = float(point[6])
        goal_poses.append(goal_pose)

    # Send goals and monitor their status
    for goal_pose in goal_poses:
        time.sleep(3)
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = goal_pose
        
        # Send the goal
        self.get_logger().info('Sending goal...')
        future = self.client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        
        if not goal_handle:
            self.get_logger().error('Failed to send goal')
            continue

        self.get_logger().info('Goal sent successfully')
        
        # Monitor the goal status
        nav_start = self.get_clock().now()
        while rclpy.ok():
            result_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(self, result_future)
            result = result_future.result()

            status = result.status

            if status == GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().info('Goal succeeded!')
                break
            elif status == GoalStatus.STATUS_CANCELED:
                self.get_logger().info('Goal was canceled!')
                break
            elif status == GoalStatus.STATUS_ABORTED:
                self.get_logger().info('Goal failed!')
                break
            else:
                self.get_logger().info(f'Unexpected result status: {status}')
                break
            now = self.get_clock().now()
            if now - nav_start > Duration(seconds=60):  # Timeout
                self.get_logger().info('Navigation task canceled due to timeout.')
                goal_handle.cancel_goal_async()
                rclpy.spin_until_future_complete(self, goal_handle.get_result_async())
                break  # Sleep to avoid busy-waiting
def main(args=None):
    rclpy.init(args=args)
    navigator = goal_navigator()
    rclpy.spin_once(navigator)
    navigator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

