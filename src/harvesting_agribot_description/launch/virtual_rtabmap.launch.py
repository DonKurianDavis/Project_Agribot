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
          'odom_frame_id':'harvesting_bot/odom',
          'publish_tf_odom':False,
          'approx_sync':True,
          'queue_size':20,
          'RGBD/Octomap':True,
          'Mem/SaveDepth16Format':"true",
          'Grid/Sensor':'1'
    }

    remappings=[
          # ('/odom','/harvesting_bot/odom'),
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

        Node(
            package = 'depthimage_to_laserscan', namespace = 'harvesting_bot' ,executable='depthimage_to_laserscan_node', output='screen',
            parameters=[{'output_frame': 'harvesting_bot/base_link'},
                        {'scan_height' : 150}],
            remappings=[('depth', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw'),
                        ('depth_camera_info', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/camera_info'),
                        ('scan','/harvesting_bot/scan')]),
        # # Node(
        #     package='robot_localization',
        #     executable='ekf_node',
        #     name='ekf_filter_node',
        #     output='screen',
        #     parameters=[os.path.join(get_package_share_directory("harvesting_agribot_description"), 'config', 'ekf.yaml')],
        # ),
    ])