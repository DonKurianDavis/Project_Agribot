import os
from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription,RegisterEventHandler,TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.event_handlers import OnProcessExit

from launch_ros.actions import Node



def generate_launch_description():

    package_name='multibot_navigation'


    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','multibot.launch.py'
                )]), launch_arguments={'use_sim_time': 'true','use_ros2_control': 'false'}.items()
    )

    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]), 
                      launch_arguments={'world': 'src/multibot_navigation/world/custom_environment.world'}.items()
             )

    fertilizer_spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py', namespace="fertilizer_bot",
                        arguments=['-topic', '/fertilizer_bot/robot_description',
                                    '-robot_namespace', 'fertilizer_bot',
                                    '-entity', 'fertilizer_bot',
                                    '-y','3.5',
                                    '-Y','-1.5707'],
                        output='screen')
    
    harvesting_spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py', namespace="harvesting_bot",
                        arguments=['-topic', '/harvesting_bot/robot_description',
                                    '-entity', 'harvesting_bot',
                                    '-robot_namespace', 'harvesting_bot',
                                    '-x','-1.0',
                                    '-y','3.5',
                                    '-Y','-1.5707'],
                        output='screen')

    harvesting_arm_controller_spawner = Node(
        package="controller_manager",
        namespace="harvesting_bot",
        executable="spawner",
        arguments=["arm_controller"],
    )

    harvesting_joint_broad_spawner = Node(
        package="controller_manager",
        namespace="harvesting_bot",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    fertilizer_arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        namespace="fertilizer_bot",
        arguments=["arm_controller"],
    )

    fertilizer_joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        namespace="fertilizer_bot",
        arguments=["joint_state_broadcaster"],
    )

    # Tried to implement ROS2 Control for Both the bots. But the camera accquires the namespace of the first bot doesn't change it even after spawning the second robot due to usage of ROS2 Control.
    delayed_controller_manager = TimerAction(period=5.0, actions=[harvesting_spawn_entity])



    return LaunchDescription([
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=fertilizer_spawn_entity,
                on_exit=[TimerAction(period=2.0, actions=[
                    fertilizer_arm_controller_spawner,
                    fertilizer_joint_broad_spawner
                ])],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=harvesting_spawn_entity,
                on_exit=[TimerAction(period=2.0, actions=[
                    harvesting_arm_controller_spawner,
                    harvesting_joint_broad_spawner
                ])],
            )
        ),
        rsp,
        gazebo,
        fertilizer_spawn_entity,
        delayed_controller_manager
    ])