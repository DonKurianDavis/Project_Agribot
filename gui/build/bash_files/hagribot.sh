#!/usr/bin/bash
tmux new-session -d -s hagribot
tmux send-keys -t hagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description robot_control.launch.py" C-m
tmux attach -t hagribot
