import os

from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch.event_handlers import OnProcessExit
from launch import LaunchDescription
from launch_ros.actions import Node, SetParameter
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument,TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    qos = LaunchConfiguration('qos')
    localization = LaunchConfiguration('localization')

    parameters={
          'frame_id':'harvesting_bot/base_link',
          'approx_sync':True,
          'subscribe_depth':True,
          'odom_frame_id':'harvesting_bot/odom',
          'Reg/Force3DoF':'true',
          'Optimizer/GravitySigma':'0',
          'database_path':'database/real.db',
          'scan_topic':'/harvesting_bot/scan',
          'subscribe_scan':False,
          'scan_topic':'/harvesting_bot/scan',
          'subscribe_scan_cloud':True,
          'RGBD/Octomap':True,
          'Grid/Sensor':'1',
          #'Grid/NormalsSegmentation':'True',
        #   'Grid/MinGroundHeight':'0.2',
          #'Grid/MaxObstacleHeight':'0.1'
        #   'Vis/MinInliers':'50'
    }

    remappings=[
          ('/harvesting_bot/rgb/image', '/harvesting_bot/harvesting_bot_camera/color/image_raw'),
          ('/harvesting_bot/scan_cloud', '/harvesting_bot/harvesting_bot_camera/depth/color/points'),
          ('/harvesting_bot/rgb/camera_info', '/harvesting_bot/harvesting_bot_camera/color/camera_info'),
          ('/harvesting_bot/depth/image', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw')]
    
    # Launch camera driver
    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('realsense2_camera'), 'examples/align_depth'),'/rs_align_depth_launch.py']),
            launch_arguments={'camera_namespace':'harvesting_bot',
                            'camera_name':'harvesting_bot_camera',
                            'depth_module.depth_profile':'640x480x30',
                            'depth_module.infra_profile':'640x480x30',
                            'rgb_camera.color_profile':'640x480x30',
                            'enable_gyro': 'true',
                            'enable_accel': 'true',
                            'unite_imu_method': '1',
                            'pointcloud.enable':'true',
                            'pointcloud.ordered_pc':'true',
                            #   'hole_filling_filter.enable':'true',
                            'json_file_path':'src/harvesting_agribot_description/config/realsense.json',
                            #   'pointcloud.allow_no_texture_points':'true',
                            'enable_sync': 'true'}.items()
    )
    # IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([os.path.join(
    #         get_package_share_directory('rtabmap_launch'), 'launch'),'/rtabmap.launch.py']),
    #         launch_arguments={'frame_id':'harvesting_bot/base_link',
    #                             'namespace':'harvesting_bot',
    #                             'localization':'false',
    #                             'use_sim_time':'false',
    #                             'rtabmap_viz':'false',
    #                             'odom_topic':'/harvesting_bot/diffbot_base_controller/odom',
    #                             'approx_sync':'true',
    #                             'subscribe_depth':'true',
    #                             'use_action_for_goal':'true',
    #                             'visual_odometry':'false',
    #                             'Reg/Force3DoF':'true',
    #                             'Optimizer/GravitySigma':'0',
    #                             'database_path':'database/real.db',
    #                             'rgb_topic':'/harvesting_bot/harvesting_bot_camera/color/image_raw',
    #                             'depth_topic':'/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw',
    #                             'camera_info_topic':'/harvesting_bot/harvesting_bot_camera/color/camera_info',
    #                             'subscribe_scan':'false',
    #                             'publish_tf_odom':'false'}.items(),
    # ),
    robot_localization=Node(
        package='robot_localization',
        executable='ekf_node',
        namespace='harvesting_bot',
        output='screen',
        parameters=[os.path.join(get_package_share_directory("harvesting_agribot_description"), 'config', 'ekf.yaml')],
        remappings=[('/harvesting_bot/odometry/filtered','/harvesting_bot/odom')]
    )
    
    depth_laser=Node(
        namespace='harvesting_bot',
        package='depthimage_to_laserscan', executable='depthimage_to_laserscan_node', output='screen',
        parameters=[{'output_frame': 'harvesting_bot/base_link'}],
        remappings=[('depth', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw'),
                    ('depth_camera_info', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/camera_info'),
                    ('scan','/harvesting_bot/scan')])
    
    imu=Node(
        namespace='harvesting_bot',
        package='imu_filter_madgwick', executable='imu_filter_madgwick_node', output='screen',
        parameters=[{'use_mag': False, 
                    'world_frame':'enu', 
                    'publish_tf':False}],
        remappings=[('imu/data_raw', '/harvesting_bot/harvesting_bot_camera/imu'),
                    ('imu/data','/harvesting_bot/imu')])

    # Nodes to launch
    rtabmap_odom=Node(
        package='rtabmap_odom', executable='rgbd_odometry', output='screen',
        namespace='harvesting_bot',
        parameters=[{'frame_id':'harvesting_bot/base_link'},
                    {'approx_sync':True},
                    {'odom_frame_id':'harvesting_bot/odom'},
                    {'publish_tf':False},
                    {'Reg/Force3DoF':'true'},
                    {'Optimizer/GravitySigma':'0'},
                    {'RGBD/Octomap':True},
                    {'Grid/Sensor':'1'}],
        remappings=[('/harvesting_bot/rgb/image', '/harvesting_bot/harvesting_bot_camera/color/image_raw'),
                    ('/harvesting_bot/rgb/camera_info', '/harvesting_bot/harvesting_bot_camera/color/camera_info'),
                    ('/harvesting_bot/depth/image', '/harvesting_bot/harvesting_bot_camera/aligned_depth_to_color/image_raw'),
                    ('odom', '/harvesting_bot/visual_odom')])
    
    # SLAM mode:
    rtabmap_slam=Node(
        condition=UnlessCondition(localization),
        namespace='harvesting_bot',
        package='rtabmap_slam', executable='rtabmap', output='screen',
        parameters=[parameters],
        remappings=remappings,
        arguments=['-d']) # This will delete the previous database (~/.ros/rtabmap.db)
    
    # Localization mode:
    rtabmap_slam_localization=Node(
        condition=IfCondition(localization),
        namespace='harvesting_bot',
        package='rtabmap_slam', executable='rtabmap', output='screen',
        parameters=[parameters,
        {'Mem/IncrementalMemory':'False',
        'Mem/InitWMWithAllNodes':'True'}],
        remappings=remappings)
    
    # Node(
    #     package='rtabmap_viz', executable='rtabmap_viz', output='screen', namespace='harvesting_bot',
    #     parameters=[parameters],
    #     remappings=remappings),
    delay_localization = TimerAction(period=5.0,actions=[robot_localization,depth_laser,imu,rtabmap_odom,rtabmap_slam,rtabmap_slam_localization])
    return LaunchDescription([
        
    DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true'),

    DeclareLaunchArgument(
        'qos', default_value='2',
        description='QoS used for input sensor topics'),

    DeclareLaunchArgument(
        'localization', default_value='false',
        description='Launch in localization mode.'),
        
    realsense_launch,
    delay_localization,
])
