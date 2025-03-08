#!/usr/bin/bash
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description robot_control.launch.py"&
sleep 10
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description mapping.launch.py"&
sleep 5
gnome-terminal -- bash -c "ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/harvesting_bot/cmd_keyboard"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && rviz2 -d nav2_config.rviz"&
# sleep 10
# gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description navigation.launch.py"&
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run twist_mux twist_mux --ros-args --params-file ./src/harvesting_agribot_description/config/twist_mux.yaml -r cmd_vel_out:=/harvesting_bot/diffbot_base_controller/cmd_vel_unstamped"&
# sleep 5
# gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run harvesting_agribot_description goal_navigator"
