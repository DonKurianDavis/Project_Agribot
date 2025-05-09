#!/usr/bin/bash
tmux kill-session -t hmagribot
tmux kill-session -t hnagribot
tmux new-session -d -s hnagribot
tmux send-keys -t hnagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description mapping.launch.py localization:=true" C-m
tmux split-window -v -t hnagribot
tmux send-keys -t hnagribot "sleep 6 && cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description navigation.launch.py" C-m
tmux split-window -h -t hnagribot
tmux send-keys -t hnagribot "sleep 12 && cd ~/Project_Agribot && source install/setup.bash &&  ros2 run harvesting_agribot_description harvesting_goal_executor" C-m
tmux split-window -v -t hnagribot
tmux send-keys -t hnagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 run harvesting_agribot_description chilly_detection --ros-args -p virtual_world:=false -r __ns:=/harvesting_bot" C-m
tmux split-window -h -t hnagribot
tmux send-keys -t hnagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 run harvesting_agribot_description disease_detection --ros-args -p virtual_world:=true -r __ns:=/harvesting_bot" C-m
tmux split-window -v -t hnagribot
tmux send-keys -t hnagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_arm_moveit_config move_group.launch.py" C-m
tmux attach -t hnagribot
