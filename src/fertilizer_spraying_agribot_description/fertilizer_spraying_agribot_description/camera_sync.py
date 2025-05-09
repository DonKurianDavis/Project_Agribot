import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from message_filters import Subscriber, ApproximateTimeSynchronizer

class StereoImageRepublisher(Node):
    def __init__(self):
        super().__init__('stereo_image_republisher')

        # Subscribers for left camera image and camera info
        self.left_image_sub = Subscriber(self, Image, '/camera_left/image_raw')
        self.left_info_sub = Subscriber(self, CameraInfo, '/camera_left/camera_info')

        # Subscribers for right camera image and camera info
        self.right_image_sub = Subscriber(self, Image, '/camera_right/image_raw')
        self.right_info_sub = Subscriber(self, CameraInfo, '/camera_right/camera_info')

        # Synchronizing left and right camera image + info pairs
        self.sync = ApproximateTimeSynchronizer(
            [self.left_image_sub, self.left_info_sub, self.right_image_sub, self.right_info_sub],
            queue_size=50, slop=0.1
        )
        self.sync.registerCallback(self.sync_callback)

        # Publishers for republished synchronized topics
        self.left_image_pub = self.create_publisher(Image, '/fertilizer_bot/fertilizer_bot_camera/left/image_raw', 10)
        self.left_info_pub = self.create_publisher(CameraInfo, '/fertilizer_bot/fertilizer_bot_camera/left/camera_info', 10)
        self.right_image_pub = self.create_publisher(Image, '/fertilizer_bot/fertilizer_bot_camera/right/image_raw', 10)
        self.right_info_pub = self.create_publisher(CameraInfo, '/fertilizer_bot/fertilizer_bot_camera/right/camera_info', 10)

    def sync_callback(self, left_img, left_info, right_img, right_info):
        # Generate a new synchronized timestamp
        new_stamp = self.get_clock().now().to_msg()

        # Assign the new timestamp to all messages
        left_img.header.stamp = new_stamp
        left_info.header.stamp = new_stamp
        right_img.header.stamp = new_stamp
        right_info.header.stamp = new_stamp

        # Publish synchronized images and camera info
        self.left_image_pub.publish(left_img)
        self.left_info_pub.publish(left_info)
        self.right_image_pub.publish(right_img)
        self.right_info_pub.publish(right_info)

        self.get_logger().info(f"Republished synchronized stereo images & camera info at {new_stamp.sec}.{new_stamp.nanosec}")

def main(args=None):
    rclpy.init(args=args)
    node = StereoImageRepublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
