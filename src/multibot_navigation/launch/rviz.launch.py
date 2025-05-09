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

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import ReplaceString


def generate_launch_description():
    fertilizer_arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        name="fertilizer_bot",
        namespace="fertilizer_bot",
        arguments=["arm_controller"],
    )

    fertilizer_joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        name="fertilizer_bot",
        namespace="fertilizer_bot",
        arguments=["joint_state_broadcaster"],
    )

    return LaunchDescription([
        fertilizer_arm_controller_spawner,
        fertilizer_joint_broad_spawner
    ])