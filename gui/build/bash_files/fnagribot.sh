#!/usr/bin/bash
tmux new-session -d -s fnagribot 
tmux send-keys -t fnagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 launch fertilizer_spraying_agribot_description mapping.launch.py localization:=true" C-m
tmux split-window -h -t fnagribot
tmux send-keys -t fnagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 launch fertilizer_spraying_agribot_description navigation.launch.py" C-m
tmux split-window -v -t fnagribot 
tmux send-keys -t fnagribot "cd ~/Project_Agribot && source install/setup.bash &&  ros2 run fertilizer_spraying_agribot_description fertilizer_goal_executor" C-m
tmux split-window -v -t fnagribot 
tmux send-keys -t fnagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 run fertilizer_spraying_agribot_description disease_detection --ros-args -p virtual_world:=false" C-m
tmux attach -t fnagribot
