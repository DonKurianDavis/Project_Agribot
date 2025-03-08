import os

from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
import launch_ros.actions

from launch import LaunchDescription
from launch_ros.actions import Node, SetParameter
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    qos = LaunchConfiguration('qos')
    localization = LaunchConfiguration('localization')

    parameters={
          'frame_id':'harvesting_bot/base_link',
          'use_sim_time':use_sim_time,
          'approx_sync':True,
          'subscribe_depth':True,
          'use_action_for_goal':True,
          'odom_frame_id':'harvesting_bot/odom',
          'publish_tf_odom':True,
          'qos_image':qos,
          'Reg/Force3DoF':'true',
          'Optimizer/GravitySigma':'0',
          'database_path':'database/real.db',
          'scan_topic':'/harvesting_bot/scan',
          'subscribe_scan':False,
          'RGBD/Octomap':True,
          'Grid/Sensor':'1'
    }

    remappings=[
          ('/harvesting_bot/rgb/image', '/harvesting_bot/harvesting_bot_camera/color/image_raw'),
          ('/harvesting_bot/rgb/camera_info', '/harvesting_bot/harvesting_bot_camera/color/camera_info'),
          ('/harvesting_bot/depth/image', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw')]
    
    return LaunchDescription([

        # Launch camera driver
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('realsense2_camera'), 'examples/align_depth'),'/rs_align_depth_launch.py']),
                launch_arguments={'camera_namespace':'harvesting_bot',
                                  'camera_name':'harvesting_bot_camera',
                                  'enable_gyro': 'true',
                                  'enable_accel': 'true',
                                  'unite_imu_method': '1',
                                  'pointcloud.enable':'true',
                                  'pointcloud.ordered_pc':'true',
                                #   'config_file':'src/harvesting_agribot_description/config/config.yaml',
                                #   'pointcloud.allow_no_texture_points':'true',
                                  'enable_sync': 'true'}.items(),
        ),
        # launch_ros.actions.Node(
        #     package='robot_localization',
        #     executable='ekf_node',
        #     name='ekf_filter_node',
        #     output='screen',
        #     parameters=[os.path.join(get_package_share_directory("harvesting_agribot_description"), 'config', 'ekf.yaml')],
        # ),
        Node(
            namespace='harvesting_bot',
            package='depthimage_to_laserscan', executable='depthimage_to_laserscan_node', output='screen',
            parameters=[{'output_frame': 'harvesting_bot/base_link'},
                        {'scan_height' : 100}],
            remappings=[('depth', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw'),
                        ('depth_camera_info', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/camera_info'),
                        ('scan','/harvesting_bot/scan')]),
        # Node(
        #     package='imu_filter_madgwick', executable='imu_filter_madgwick_node', output='screen',
        #     parameters=[{'use_mag': False, 
        #                  'world_frame':'enu', 
        #                  'publish_tf':False}],
        #     remappings=[('imu/data_raw', '/camera/camera/imu'),
        #                 ('imu/data','/rtabmap/imu')]),
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
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
            namespace='harvesting_bot',
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters],
            remappings=remappings,
            arguments=['-d']), # This will delete the previous database (~/.ros/rtabmap.db)

        # Localization mode:
        Node(
            condition=IfCondition(localization),
            namespace='harvesting_bot',
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters,
              {'Mem/IncrementalMemory':'False',
               'Mem/InitWMWithAllNodes':'True'}],
            remappings=remappings),

        # Node(
        #     package='rtabmap_viz', executable='rtabmap_viz', output='screen',
        #     parameters=[parameters],
        #     remappings=remappings),
    
])
