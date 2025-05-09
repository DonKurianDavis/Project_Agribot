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
          'frame_id':'fertilizer_bot/base_link',
          'approx_sync':True,
          'subscribe_depth':True,
          'odom_frame_id':'fertilizer_bot/odom',
          'Reg/Force3DoF':'true',
          'Optimizer/GravitySigma':'0',
          'database_path':'database/real.db',
          'scan_topic':'/fertilizer_bot/scan',
          'subscribe_scan':False,
          'scan_topic':'/fertilizer_bot/scan',
          'subscribe_scan_cloud':True,
          'RGBD/Octomap':True,
          'Grid/Sensor':'1'
    }

    remappings=[
          ('/fertilizer_bot/rgb/image', '/fertilizer_bot/fertilizer_bot_camera/color/image_raw'),
          ('/fertilizer_bot/scan_cloud', '/fertilizer_bot/fertilizer_bot_camera/depth/color/points'),
          ('/fertilizer_bot/rgb/camera_info', '/fertilizer_bot/fertilizer_bot_camera/color/camera_info'),
          ('/fertilizer_bot/depth/image', '/fertilizer_bot/fertilizer_bot_camera/aligned_depth_to_color/image_raw')]
    
    return LaunchDescription([

        # Launch camera driver
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('realsense2_camera'), 'examples/align_depth'),'/rs_align_depth_launch.py']),
                launch_arguments={'camera_namespace':'fertilizer_bot',
                                  'camera_name':'fertilizer_bot_camera',
                                  'depth_module.depth_profile':'640x480x30',
                                  'depth_module.infra_profile':'640x480x30',
                                  'rgb_camera.color_profile':'640x480x30',
                                  'enable_gyro': 'true',
                                  'enable_accel': 'true',
                                  'unite_imu_method': '1',
                                  'pointcloud.enable':'true',
                                  'pointcloud.ordered_pc':'true',
                                #   'hole_filling_filter.enable':'true',
                                  'json_file_path':'src/fertilizer_spraying_agribot_description/config/realsense.json',
                                #   'pointcloud.allow_no_texture_points':'true',
                                  'enable_sync': 'true'}.items(),
        ),
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource([os.path.join(
        #         get_package_share_directory('rtabmap_launch'), 'launch'),'/rtabmap.launch.py']),
        #         launch_arguments={'frame_id':'fertilizer_bot/base_link',
        #                             'namespace':'fertilizer_bot',
        #                             'localization':'false',
        #                             'use_sim_time':'false',
        #                             'rtabmap_viz':'false',
        #                             'odom_topic':'/fertilizer_bot/diffbot_base_controller/odom',
        #                             'approx_sync':'true',
        #                             'subscribe_depth':'true',
        #                             'use_action_for_goal':'true',
        #                             'visual_odometry':'false',
        #                             'Reg/Force3DoF':'true',
        #                             'Optimizer/GravitySigma':'0',
        #                             'database_path':'database/real.db',
        #                             'rgb_topic':'/fertilizer_bot/fertilizer_bot_camera/color/image_raw',
        #                             'depth_topic':'/fertilizer_bot/fertilizer_bot_camera/aligned_depth_to_color/image_raw',
        #                             'camera_info_topic':'/fertilizer_bot/fertilizer_bot_camera/color/camera_info',
        #                             'subscribe_scan':'false',
        #                             'publish_tf_odom':'false'}.items(),
        # ),
        launch_ros.actions.Node(
            package='robot_localization',
            executable='ekf_node',
            namespace='fertilizer_bot',
            output='screen',
            parameters=[os.path.join(get_package_share_directory("fertilizer_spraying_agribot_description"), 'config', 'ekf.yaml')],
            remappings=[('/fertilizer_bot/odometry/filtered','/fertilizer_bot/odom')]
        ),
        Node(
            namespace='fertilizer_bot',
            package='depthimage_to_laserscan', executable='depthimage_to_laserscan_node', output='screen',
            parameters=[{'output_frame': 'fertilizer_bot/base_link'},
                        {'scan_height' : 100}],
            remappings=[('depth', '/fertilizer_bot/fertilizer_bot_camera/aligned_depth_to_color/image_raw'),
                        ('depth_camera_info', '/fertilizer_bot/fertilizer_bot_camera/aligned_depth_to_color/camera_info'),
                        ('scan','/fertilizer_bot/scan')]),
        # Node(
        #     namespace='fertilizer_bot',
        #     package='imu_filter_madgwick', executable='imu_filter_madgwick_node', output='screen',
        #     parameters=[{'use_mag': False, 
        #                  'world_frame':'enu', 
        #                  'publish_tf':False}],
        #     remappings=[('imu/data_raw', '/fertilizer_bot/fertilizer_bot_camera/imu'),
        #                 ('imu/data','/fertilizer_bot/imu')]),
                        
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
        Node(
            package='rtabmap_odom', executable='rgbd_odometry', output='screen',
            namespace='fertilizer_bot',
            parameters=[{'frame_id':'fertilizer_bot/base_link'},
                        {'approx_sync':True},
                        {'odom_frame_id':'fertilizer_bot/odom'},
                        {'publish_tf':False},
                        {'Reg/Force3DoF':'true'},
                        {'Optimizer/GravitySigma':'0'},
                        {'RGBD/Octomap':True},
                        {'Grid/Sensor':'1'}],
            remappings=[('/fertilizer_bot/rgb/image', '/fertilizer_bot/fertilizer_bot_camera/color/image_raw'),
                        ('/fertilizer_bot/rgb/camera_info', '/fertilizer_bot/fertilizer_bot_camera/color/camera_info'),
                        ('/fertilizer_bot/depth/image', '/fertilizer_bot/fertilizer_bot_camera/aligned_depth_to_color/image_raw'),
                        ('odom', '/fertilizer_bot/visual_odom')]),
    
        # SLAM mode:
        Node(
            condition=UnlessCondition(localization),
            namespace='fertilizer_bot',
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters],
            remappings=remappings,
            arguments=['-d']), # This will delete the previous database (~/.ros/rtabmap.db)

        # Localization mode:
        Node(
            condition=IfCondition(localization),
            namespace='fertilizer_bot',
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters,
              {'Mem/IncrementalMemory':'False',
               'Mem/InitWMWithAllNodes':'True'}],
            remappings=remappings),
        
        # Node(
        #     package='rtabmap_viz', executable='rtabmap_viz', output='screen', namespace='fertilizer_bot',
        #     parameters=[parameters],
        #     remappings=remappings),
    
])
