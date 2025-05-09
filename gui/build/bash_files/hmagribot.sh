#!/usr/bin/bash
tmux new-session -d -s hmagribot
tmux send-keys -t hmagribot "cd ~/Project_Agribot && source install/setup.bash && ros2 launch harvesting_agribot_description mapping.launch.py" C-m
tmux attach -t hmagribot