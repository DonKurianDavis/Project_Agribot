import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import RegisterEventHandler, TimerAction, IncludeLaunchDescription
from launch.substitutions import Command
from launch.event_handlers import OnProcessStart

from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare



def generate_launch_description():
    
    package_name='fertilizer_spraying_agribot_description'
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','bot.launch.py'
                )]), launch_arguments={'use_sim_time': 'false','use_ros2_control': 'true'}.items()
    )
    
    robot_description = Command(['ros2 param get --hide-type fertilizer_bot/robot_state_publisher robot_description'])

    robot_controllers = os.path.join(get_package_share_directory(package_name),'config','bot_controller.yaml')
    twist_mux_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux.yaml')
    twist_mux = Node(
            package="twist_mux",
            executable="twist_mux",
            parameters=[twist_mux_params],
            remappings=[('/cmd_vel_out','/fertilizer_bot/diffbot_base_controller/cmd_vel_unstamped')]
        )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        namespace="fertilizer_bot",
        parameters=[{'robot_description': robot_description}, robot_controllers],
        output="both",
    )

    delayed_controller_manager = TimerAction(period=5.0, actions=[control_node])

    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        namespace="fertilizer_bot",
        arguments=["diffbot_base_controller"],
    )

    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=control_node,
            on_start=[diff_drive_spawner],
        )
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        namespace="fertilizer_bot",
        arguments=["joint_state_broadcaster"],
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=control_node,
            on_start=[joint_broad_spawner],
        )
    )

    nodes = [
        rsp,
        twist_mux,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner
    ]

    return LaunchDescription(nodes)
