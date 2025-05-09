#!/usr/bin/bash
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch multibot_navigation gazebo.launch.py"&
sleep 2
# gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run twist_mux twist_mux --ros-args --params-file ./src/fertilizer_spraying_agribot_description/config/twist_mux.yaml -r cmd_vel_out:=/fertilizer_bot/cmd_vel"&
# sleep 2
# gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run twist_mux twist_mux --ros-args --params-file ./src/harvesting_agribot_description/config/twist_mux.yaml -r cmd_vel_out:=/harvesting_bot/cmd_vel"&
# sleep 2
gnome-terminal -- bash -c "rviz2 -d nav2.config.rviz"&
sleep 2
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description virtual_rtabmap.launch.py localization:=true"
# gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run fertilizer_spraying_agribot_description goal_navigator"
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description navigation.launch.py use_sim_time:=true"
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash &&  ros2 run multibot_navigation harvesting_goal_navigator --ros-args -p virtual_world:=true"
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run harvesting_agribot_description chilly_detection --ros-args -p virtual_world:=true"
sleep 5
gnome-terminal -- bash -c "cd ~/Project_Agribot && source install/setup.bash && ros2 run harvesting_agribot_description disease_detection --ros-args -p virtual_world:=true"
# sleep 5
# gnome-terminal -- bash -c ""