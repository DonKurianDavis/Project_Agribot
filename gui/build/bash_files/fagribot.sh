#!/usr/bin/bash
tmux new-session -d -s fagribot
tmux send-keys -t fagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 launch fertilizer_spraying_agribot_description robot_control.launch.py" C-m
tmux attach -t fagribot
