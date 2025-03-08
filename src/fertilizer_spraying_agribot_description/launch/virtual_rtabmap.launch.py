from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node

def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    qos = LaunchConfiguration('qos')
    localization = LaunchConfiguration('localization')

    parameters={
          'frame_id':'fertilizer_bot/base_link',
          'use_sim_time':use_sim_time,
          'subscribe_depth':True,
          'use_action_for_goal':True,
          'qos_image':qos,
          'qos_imu':qos,
          'Reg/Force3DoF':'true',
          'Optimizer/GravitySigma':'0',
          'database_path':'database/virtual.db',
        #   'RGBD/OptimizeMaxError':"5.0",
        #   'odom_topic':'/fertilizer_bot/odom',
          'publish_tf_odom':False,
          'approx_sync':True,
          'subscribe_scan':False,
          'scan_topic':'/fertilizer_bot/scan',
          'RGBD/Octomap':True,
          'Mem/SaveDepth16Format':"true",
          'Grid/Sensor':'1'
    }

    remappings=[
          ('odom','/fertilizer_bot/odom'),
        #   ('/fertilizer_bot/map','/map'),
          ('rgb/image', '/fertilizer_bot/fertilizer_bot_camera/color/image_raw'),
          ('rgb/camera_info', '/fertilizer_bot/fertilizer_bot_camera/color/camera_info'),
          ('depth/image', '/fertilizer_bot/fertilizer_bot_camera/aligned_depth_to_color/image_raw')]
    
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

        Node(
            condition=UnlessCondition(localization),
            package='rtabmap_slam', 
            executable='rtabmap', 
            output='screen',
            namespace='fertilizer_bot',
            parameters=[parameters],
            remappings=remappings,
            arguments=['-d']), # This will delete the previous database (~/.ros/rtabmap.db)

        # Localization mode:
        Node(
            condition=IfCondition(localization),
            package='rtabmap_slam', 
            executable='rtabmap', 
            namespace='fertilizer_bot',
            output='screen',
            parameters=[parameters,
              {'Mem/IncrementalMemory':'False',
               'Mem/InitWMWithAllNodes':'True'}],
            remappings=remappings),

        Node(
            namespace='fertilizer_bot',
            package='depthimage_to_laserscan', executable='depthimage_to_laserscan_node', output='screen',
            parameters=[{'output_frame': 'fertilizer_bot/base_link'}],
            remappings=[('depth', '/fertilizer_bot/fertilizer_bot_camera/aligned_depth_to_color/image_raw'),
                        ('depth_camera_info', '/fertilizer_bot/fertilizer_bot_camera/aligned_depth_to_color/camera_info'),
                        ('scan','/fertilizer_bot/scan')]),
    ])