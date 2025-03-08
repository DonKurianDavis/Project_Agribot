#!/usr/bin/bash
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch multibot_navigation gazebo.launch.py"&
sleep 5
gnome-terminal -- bash -c "ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/harvesting_bot/cmd_vel -r __ns:=/harvesting_bot"&
sleep 5
gnome-terminal -- bash -c "ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/fertilizer_bot/cmd_vel -r __ns:=/fertilizer_bot"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && rviz2 -d nav2.config.rviz "&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch fertilizer_spraying_agribot_description virtual_rtabmap.launch.py localization:=true"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description virtual_rtabmap.launch.py localization:=true"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch fertilizer_spraying_agribot_description navigation.launch.py use_sim_time:=true"&
sleep 10
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description navigation.launch.py use_sim_time:=true"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run harvesting_agribot_description disease_detection --ros-args -p virtual_world:=true"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash &&  ros2 run multibot_navigation harvesting_goal_navigator --ros-args -p virtual_world:=true"
# sleep 120
# gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash &&  ros2 run multibot_navigation fertilizer_goal_navigator --ros-args -p virtual_world:=true"