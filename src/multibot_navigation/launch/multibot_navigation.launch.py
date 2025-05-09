# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Example for spawning multiple robots in Gazebo.

This is an example on how to create a launch file for spawning multiple robots into Gazebo
and launch multiple instances of the navigation stack, each controlling one robot.
The robots co-exist on a shared environment and are controlled by independent nav stacks.
"""

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess, GroupAction,
                            IncludeLaunchDescription, LogInfo)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution


def generate_launch_description():
    pkg_dir = get_package_share_directory('multibot_navigation')
    launch_dir = os.path.join(pkg_dir, 'launch')
    declare_fertilizer_bot_params_file_cmd = DeclareLaunchArgument(
        'fertilizer_bot_params_file',
        default_value=os.path.join(pkg_dir, 'config', 'nav2_multirobot_params_1.yaml'),
        description='Full path to the ROS2 parameters file to use for robot1 launched nodes')

    declare_harvesting_bot_params_file_cmd = DeclareLaunchArgument(
        'harvesting_bot_params_file',
        default_value=os.path.join(pkg_dir, 'config', 'nav2_multirobot_params_2.yaml'),
        description='Full path to the ROS2 parameters file to use for robot2 launched nodes')
    robots = [
        {'name': 'fertilizer_bot', 'x_pose': 0.0, 'y_pose': 3.5, 'z_pose': 0.01,
                           'roll': 0.0, 'pitch': 0.0, 'yaw': -1.5707},
        {'name': 'harvesting_bot', 'x_pose': -1.0, 'y_pose': 3.5, 'z_pose': 0.01,
                           'roll': 0.0, 'pitch': 0.0, 'yaw': -1.5707}]
    fertilizer_bot_params_file = LaunchConfiguration("fertilizer_bot_params_file")
    fertilizer_bot = IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(launch_dir, 'navigation.launch.py')),
                                launch_arguments={'namespace':'fertilizer_bot',
                                                'params_file':fertilizer_bot_params_file})
    harvesting_bot_params_file = LaunchConfiguration("harvesting_bot_params_file")
    harvesting_bot = IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(launch_dir, 'navigation.launch.py')),
                                launch_arguments={'namespace':'harvesting_bot',
                                                'params_file':harvesting_bot_params_file})
    
    ld = LaunchDescription()
    ld.add_action(declare_fertilizer_bot_params_file_cmd)
    # ld.add_action(declare_harvesting_bot_params_file_cmd)
    ld.add_action(fertilizer_bot)
    # ld.add_action(harvesting_bot)

    return ld