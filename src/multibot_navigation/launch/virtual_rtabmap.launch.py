from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node

def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    qos = LaunchConfiguration('qos')
    localization = LaunchConfiguration('localization')

    harvesting_parameters={
          'frame_id':'harvesting_bot/base_link',
          'use_sim_time':use_sim_time,
          'namespace':'harvesting_bot',
          'approx_sync':False,
          'subscribe_depth':True,
          'use_action_for_goal':True,
          'qos_image':qos,
          'qos_imu':qos,
          'Reg/Force3DoF':'true',
          'Optimizer/GravitySigma':'0',
          'database_path':'database/virtual.db',
    }

    harvesting_remappings=[
          ('/odom','/harvesting_bot/odom'),
        #   ('rtabmap/map','/map'),
          ('rgb/image', '/harvesting_bot/camera/image_raw'),
          ('rgb/camera_info', '/harvesting_bot/camera/camera_info'),
          ('depth/image', '/harvesting_bot/camera/depth/image_raw')]
    
    fertilizer_parameters={
          'frame_id':'fertilizer_bot/base_link',
          'use_sim_time':use_sim_time,
          'namespace':'fertilizer_bot',
          'approx_sync':False,
          'subscribe_depth':True,
          'use_action_for_goal':True,
          'qos_image':qos,
          'qos_imu':qos,
          'Reg/Force3DoF':'true',
          'Optimizer/GravitySigma':'0',
          'database_path':'database/virtual.db',
    }

    fertilizer_remappings=[
          ('/odom','/fertilizer_bot/odom'),
        #   ('rtabmap/map','/map'),
          ('rgb/image', '/fertilizer_bot/camera/image_raw'),
          ('rgb/camera_info', '/fertilizer_bot/camera/camera_info'),
          ('depth/image', '/fertilizer_bot/camera/depth/image_raw')]

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
            name='harvesting_bot',
            namespace='harvesting_bot',
            executable='rtabmap', 
            output='screen',
            parameters=[harvesting_parameters],
            remappings=harvesting_remappings,
            arguments=['-d']), # This will delete the previous database (~/.ros/rtabmap.db)

        # Localization mode:
        Node(
            condition=IfCondition(localization),
            package='rtabmap_slam', 
            executable='rtabmap', 
            output='screen',
            name='harvesting_bot',
            namespace='harvesting_bot',
            parameters=[harvesting_parameters,
              {'Mem/IncrementalMemory':'False',
               'Mem/InitWMWithAllNodes':'True'}],
            remappings=harvesting_remappings),

        Node(
            package='rtabmap_viz', 
            executable='rtabmap_viz', 
            output='screen',
            namespace='harvesting_bot',
            name='harvesting_bot',
            parameters=[harvesting_parameters],
            remappings=harvesting_remappings),

        Node(
            condition=UnlessCondition(localization),
            package='rtabmap_slam', 
            executable='rtabmap', 
            output='screen',
            namespace='fertilizer_bot',
            name='fertilizer_bot',
            parameters=[fertilizer_parameters],
            remappings=fertilizer_remappings,
            arguments=['-d']), # This will delete the previous database (~/.ros/rtabmap.db)

        # Localization mode:
        Node(
            condition=IfCondition(localization),
            package='rtabmap_slam', 
            executable='rtabmap', 
            output='screen',
            name='fertilizer_bot',
            namespace='fertilizer_bot',
            parameters=[fertilizer_parameters,
              {'Mem/IncrementalMemory':'False',
               'Mem/InitWMWithAllNodes':'True'}],
            remappings=fertilizer_remappings),

        Node(
            package='rtabmap_viz', 
            executable='rtabmap_viz', 
            output='screen',
            name='fertilizer_bot',
            namespace='fertilizer_bot',
            parameters=[fertilizer_parameters],
            remappings=fertilizer_remappings),
    ])