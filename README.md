# Part3

# Overview
The goal to the project is to find the kaggle in a map. There are two robot with A* algorithm to find the kaggle together.
The A* heuristic is manhattan distance.
Two Bot will regard each other as a block.
Bot A's target is kaggle, while Bot B's target is Bot A initially
If the Bot B's distance to kaggle is less than 5 step, Bot B's target becomes kaggle.

# How to run

main.py
-------
You can change the variable **RENDER_FLAG** to determine if you want the experienment mode or render mode.
ender mode: Only execute twice, first time will domestrate how two bot work together, second time will domestrate only Bot A working as comparison.
Experienment mdoe: The mode will domestrate how it work if there are 1000 kaggle(default, you can change it).

Map size: You can adjust the variable **GRID_R** and **GRID_C** to whatever you want.

MAX_MISSION: This variable means how many kaggles are there, but you can change it in **Render Mode**.
MAX_STEPS_PER_MISSION: This variable is the limit step to a mission.

execute
-------
python pygame
python main.py

# Dependencies

pygame
------
Graph Render and environment simulate

sprites
-------
Render the picture of bot, floor and kaggle