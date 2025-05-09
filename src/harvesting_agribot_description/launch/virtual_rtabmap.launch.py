from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    qos = LaunchConfiguration('qos')
    localization = LaunchConfiguration('localization')

    parameters={
          'frame_id':'harvesting_bot/base_link',
          'use_sim_time':use_sim_time,
          'subscribe_depth':True,
          'rtabmap_viz':False,
          'use_action_for_goal':True,
          'qos_image':qos,
          'Reg/Force3DoF':'true',
          'Optimizer/GravitySigma':'0',
          'database_path':'database/virtual.db',
        #   'odom_frame_id':'harvesting_bot/odom',
          'publish_tf':False,
          'approx_sync':True,
          'queue_size':20,
          'RGBD/Octomap':True,
          'Mem/SaveDepth16Format':"true",
          'Grid/Sensor':'1',
          'RGBD/OptimizeMaxError':"0.0",
    }

    remappings=[
          ('odom','/harvesting_bot/diffbot_base_controller/odom'),
        #   ('/harvesting_bot/map','/map'),
          ('rgb/image', '/harvesting_bot/harvesting_bot_camera/color/image_raw'),
          ('rgb/camera_info', '/harvesting_bot/harvesting_bot_camera/color/camera_info'),
          ('depth/image', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw')]
    
    return LaunchDescription([

        # Launch arguments
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument(
            'qos', default_value='2',
            description='QoS used for input sensor topics'),

        DeclareLaunchArgument(
            'localization', default_value='false',
            description='Launch in localization mode.'),

        # Nodes to launch

        # SLAM mode:
        Node(
            condition=UnlessCondition(localization),
            package='rtabmap_slam', 
            executable='rtabmap', 
            namespace='harvesting_bot',
            output='screen',
            parameters=[parameters],
            remappings=remappings,
            arguments=['-d']), # This will delete the previous database (~/.ros/rtabmap.db)

        # Localization mode:
        Node(
            condition=IfCondition(localization),
            package='rtabmap_slam', 
            executable='rtabmap', 
            output='screen',
            namespace='harvesting_bot',
            parameters=[parameters,
              {'Mem/IncrementalMemory':'False',
               'Mem/InitWMWithAllNodes':'True'}],
            remappings=remappings),

        # Node(
        #     package='rtabmap_odom', executable='rgbd_odometry', output='screen',
        #     namespace='harvesting_bot',
        #     parameters=[{'frame_id':'harvesting_bot/base_link'},
        #                 {'approx_sync':True},
        #                 {'odom_frame_id':'harvesting_bot/odom'},
        #                 {'publish_tf_odom':False},
        #                 {'qos_image':qos},
        #                 {'Reg/Force3DoF':'true'},
        #                 {'Optimizer/GravitySigma':'0'},
        #                 {'RGBD/Octomap':True},
        #                 {'Grid/Sensor':'1'}],
        #     remappings=[('/harvesting_bot/rgb/image', '/harvesting_bot/harvesting_bot_camera/color/image_raw'),
        #                 ('/harvesting_bot/rgb/camera_info', '/harvesting_bot/harvesting_bot_camera/color/camera_info'),
        #                 ('/harvesting_bot/depth/image', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw'),
        #                 ('/harvesting_bot/odom', '/harvesting_bot/visual_odom')]),
    
        Node(
            package = 'depthimage_to_laserscan', namespace = 'harvesting_bot' ,executable='depthimage_to_laserscan_node', output='screen',
            parameters=[{'output_frame': 'harvesting_bot/base_link'},
                        {'scan_height' : 150}],
            remappings=[('depth', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw'),
                        ('depth_camera_info', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/camera_info'),
                        ('scan','/harvesting_bot/scan')]),

        Node(
            package= 'tf2_ros', namespace='harvesting_bot', executable='static_transform_publisher',
            arguments=["0", "0", "0", "0", "0", "0", "map", "harvesting_bot/odom"],
            output="screen"
        )         
        # Node(
        #     package='robot_localization',executable='ekf_node',namespace="harvesting_bot",
        #     output='screen',
        #     parameters=[os.path.join(get_package_share_directory("harvesting_agribot_description"), 'config', 'ekf.yaml')]),
    ])