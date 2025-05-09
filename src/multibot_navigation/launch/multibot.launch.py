import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node

import xacro

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_ros2_control = LaunchConfiguration('use_ros2_control')
    fertilizer_pkg_path = os.path.join(get_package_share_directory('fertilizer_spraying_agribot_description'))
    fertilizer_agribot = os.path.join(fertilizer_pkg_path,'urdf','fertilizer_spraying_agribot.xacro')
    harvesting_pkg_path = os.path.join(get_package_share_directory('harvesting_agribot_description'))
    harvesting_agribot = os.path.join(harvesting_pkg_path,'urdf','harvesting_agribot.xacro')
    # harvesting_robot_description_config = xacro.process_file(harvesting_agribot).toxml()
    harvesting_robot_description_config = Command(['xacro ', harvesting_agribot, ' use_ros2_control:=', use_ros2_control])
    fertilizer_robot_description_config = Command(['xacro ', fertilizer_agribot, ' use_ros2_control:=', use_ros2_control])
    harvesting_params = {'robot_description':harvesting_robot_description_config, 'use_sim_time': use_sim_time}
    fertilizer_params = {'robot_description':fertilizer_robot_description_config, 'use_sim_time': use_sim_time}
    harvesting_robot_state_publisher = Node( 
        package = 'robot_state_publisher',
        executable = 'robot_state_publisher',
        namespace='harvesting_bot',
        output = 'screen',
        parameters = [harvesting_params]
    )
    fertilizer_robot_state_publisher = Node( 
        package = 'robot_state_publisher',
        executable = 'robot_state_publisher',
        namespace='fertilizer_bot',
        output = 'screen',
        parameters = [fertilizer_params]
    )
    harvesting_joint_state_publisher = Node( 
        package = 'joint_state_publisher',
        executable = 'joint_state_publisher',
        namespace='harvesting_bot',
        output = 'screen',
        parameters = [harvesting_params]
    )
    fertilizer_joint_state_publisher = Node( 
        package = 'joint_state_publisher',
        executable = 'joint_state_publisher',
        namespace='fertilizer_bot',
        output = 'screen',
        parameters = [fertilizer_params]
    )
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description="use_sim_time which if set to True will indicate to the node to begin subscribing to the /clock topic and synchronizing to the published simulation time"),
        DeclareLaunchArgument(
            'use_ros2_control',
            default_value='false',
            description='Use ros2_control if true'),
            
        harvesting_robot_state_publisher,
        fertilizer_robot_state_publisher,
        harvesting_joint_state_publisher,
        fertilizer_joint_state_publisher

    ])