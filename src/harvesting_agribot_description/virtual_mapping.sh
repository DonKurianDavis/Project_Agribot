#!/usr/bin/bash
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description gazebo.launch.py"&
sleep 5
gnome-terminal -- bash -c "ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/harvesting_bot/cmd_vel -r __ns:=/harvesting_bot"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && rviz2"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description virtual_rtabmap.launch.py"&
# sleep 5
# gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run harvesting_agribot_description plant_points"
