#!/usr/bin/bash
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description gazebo.launch.py"&
sleep 5
gnome-terminal -- bash -c "ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/harvesting_bot/cmd_vel -r __ns:=/harvesting_bot"&
# gnome-terminal -- bash -c "ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/fertilizer_bot/cmd_vel -r __ns:=fertilizer_bot"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && rviz2 -d nav2.config.rviz "&
# gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch fertilizer_spraying_agribot_description virtual_rtabmap.launch.py"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description virtual_rtabmap.launch.py"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run multibot_navigation plant_points --ros-args -p virtual_world:=true"&