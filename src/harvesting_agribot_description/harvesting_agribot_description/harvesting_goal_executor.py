#!/usr/bin/env python3
from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from std_msgs.msg import String, Int16

class HarvestingGoalExecutor(Node):
    def __init__(self):
        super().__init__('harvesting_bot_goal_executor')
        self.create_subscription(PoseStamped, "/harvesting_bot/goal_location", self.goal_executor, 10)
        self.goal_publisher = self.create_publisher(String, '/harvesting_bot/goal_status', 10)
        self.client = ActionClient(self, NavigateToPose, 'harvesting_bot/navigate_to_pose')
        
        self.get_logger().info("Waiting for NavigateToPose action server...")
        self.client.wait_for_server(timeout_sec=5.0)
        
    def goal_executor(self, goal_pose: PoseStamped):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = goal_pose

        self.get_logger().info("Sending goal...")
        
        # Send goal asynchronously
        future = self.client.send_goal_async(goal_msg)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        msg = String()

        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error("Goal rejected by server")
            msg.data = "GOAL REJECTED"
            self.goal_publisher.publish(msg)
            return

        self.get_logger().info("Goal accepted, waiting for result...")
        
        # Attach callback for result
        goal_handle.get_result_async().add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result()
        msg = String()

        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Goal succeeded!")
            msg.data = "GOAL REACHED"
        elif result.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("Goal was canceled!")
            msg.data = "GOAL CANCELED"
        elif result.status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info("Goal failed!")
            msg.data = "GOAL FAILED"
        else:
            self.get_logger().info(f"Unexpected result status: {result.status}")
            msg.data = "GOAL FAILED"

        self.goal_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = HarvestingGoalExecutor()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
