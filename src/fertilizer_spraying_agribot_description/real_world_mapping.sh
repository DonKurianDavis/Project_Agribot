#!/usr/bin/bash
gnome-terminal -- bash -c "cd ~/Project_Agribot/src/fertilizer_spraying_agribot_description && source install/setup.bash && ros2 launch fertilizer_spraying_agribot_description robot_control.launch.py"&
sleep 10
gnome-terminal -- bash -c "cd ~/Project_Agribot/src/fertilizer_spraying_agribot_description && source install/setup.bash && ros2 launch fertilizer_spraying_agribot_description mapping.launch.py"&
sleep 10
gnome-terminal -- bash -c "ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diffbot_base_controller/cmd_vel_unstamped"&
sleep 10
gnome-terminal -- bash -c "cd ~/Project_Agribot/src/fertilizer_spraying_agribot_description && rviz2"
# sleep 10
# gnome-terminal -- bash -c "cd ~/Project_Agribot/src/fertilizer_spraying_agribot_description && source install/setup.bash && ros2 run fertilizer_spraying_agribot_description plant_points"
