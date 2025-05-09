import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from message_filters import Subscriber, ApproximateTimeSynchronizer
import cv2
import numpy as np
from cv_bridge import CvBridge

bridge = CvBridge()

class StereoImageProcessor(Node):
    def __init__(self):
        super().__init__('stereo_image_processor')

        # Subscribers for rectified images
        self.left_image_sub = Subscriber(self, Image, '/fertilizer_bot/fertilizer_bot_camera/left/image_rect')
        self.right_image_sub = Subscriber(self, Image, '/fertilizer_bot/fertilizer_bot_camera/right/image_rect')

        # Synchronize rectified images
        self.sync = ApproximateTimeSynchronizer(
            [self.left_image_sub, self.right_image_sub], queue_size=10, slop=0.1
        )
        self.sync.registerCallback(self.process_stereo)

        # Publisher for disparity
        self.disparity_pub = self.create_publisher(Image, '/stereo/disparity', 10)

        # Stereo SGBM settings
        self.stereo = cv2.StereoSGBM.create(
            minDisparity=0,
            numDisparities=128,  # Increase for better depth range
            blockSize=9,  # Reduce block size for finer details
            P1=8 * 3 * 9**2,
            P2=32 * 3 * 9**2,
            disp12MaxDiff=1,
            uniquenessRatio=10,
            speckleWindowSize=20,
            speckleRange=32,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
        )

    def process_stereo(self, left_msg, right_msg):
        # Convert to OpenCV format
        left_img = bridge.imgmsg_to_cv2(left_msg)  # Already rectified, no need for color conversion
        right_img = bridge.imgmsg_to_cv2(right_msg)

        # Compute disparity
        disparity = self.stereo.compute(left_img, right_img).astype(np.float32) / 16.0

        # Normalize for visualization
        disparity_normalized = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

        # Convert to ROS message
        disparity_msg = bridge.cv2_to_imgmsg(disparity_normalized, encoding="mono8")

        # Publish disparity
        self.disparity_pub.publish(disparity_msg)
        self.get_logger().info("Published disparity map")

def main(args=None):
    rclpy.init(args=args)
    node = StereoImageProcessor()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()