import os
from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node



def generate_launch_description():

    package_name='fertilizer_spraying_agribot_description'


    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','bot.launch.py'
                )]), launch_arguments={'use_sim_time': 'true','use_ros2_control': 'false'}.items()
    )

    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]), 
                      launch_arguments={'world': 'src/fertilizer_spraying_agribot_description/world/custom_environment.world'}.items()
             )

    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', '/fertilizer_bot/robot_description',
                                    '-robot_namespace', 'fertilizer_bot',
                                    '-entity', 'fertilizer_bot',
                                    '-y','3.5',
                                    '-Y','-1.5707'],
                        output='screen')

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        # arm_controller_spawner,
        # joint_broad_spawner
    ])