'''
Part 3 : 雙機器人協作任務
'''
from warehouse_robot import WarehouseRobot, RobotAction
from agents import BotTypeA, BotTypeB
import time
import random
import sys
import pygame 

RENDER_FLAG = 1 # 0 for experienment mdoe; 1 for render mdoe

# map size
GRID_R, GRID_C = 10, 10

if RENDER_FLAG == 1:
    print("--- RENDER MODE ---")
    FPS = 4
    MAX_MISSIONS = 1
    MAX_STEPS_PER_MISSION = 500 # max step
else:
    print("--- EXPERIENMENT MODE ---")
    FPS = 0
    MAX_MISSIONS = 100
    MAX_STEPS_PER_MISSION = 300

def run_mission(env: WarehouseRobot, team: list, team_name: str, render_mode):
    
    env.reset()
    for bot in team:
        bot.reset_agent()
    
    steps = 0
    mission_complete = False
    hero = None
    
    while not mission_complete:
        
        all_robot_positions = env.robot_positions 
        target_pos = env.target_pos
        
        for i, bot in enumerate(team):
            
            action = bot.get_action(
                my_index=i, 
                all_robot_positions=all_robot_positions, 
                target_pos=target_pos,
                grid_rows=GRID_R, 
                grid_cols=GRID_C
            )
            
            found_package = env.perform_action(i, action)
            
            if render_mode:
                info_text = f"[{team_name}] Step: {steps + 1}. {bot.name}: {action.name}"
                env.render(info_text)
            
            if found_package:
                hero = bot.name
                mission_complete = True
                break
        
        steps += 1
        
        if steps > MAX_STEPS_PER_MISSION:
            mission_complete = True
            steps = MAX_STEPS_PER_MISSION
            if render_mode:
                env.render("Mission Timeout!")
            break

    if render_mode and steps < MAX_STEPS_PER_MISSION:
        env.render(f"Mission Complete! Found by {hero} in {steps} steps. ({team_name})")
        time.sleep(3)
    
    return steps

def run_experiment():
    
    # 1. initialize
    render_mode_bool = (RENDER_FLAG == 1)
    
    print("==================================================")
    if RENDER_FLAG == 1:
        print("FIND KAGGLE WITH RENDER MODE(2 rounds)")
    else:
        print(f"FIND KAGGEL WITH EXPERIENMENT MODE( {MAX_MISSIONS} rounds)")
    print("==================================================")
    
    # Bot A + Bot B
    env_collaboration = WarehouseRobot(grid_rows=GRID_R, grid_cols=GRID_C, fps=FPS)
    team_collaboration = [
        BotTypeA("P1 (A* main)", grid_rows=GRID_R, grid_cols=GRID_C),
        BotTypeB("P2 (A* supporter)", grid_rows=GRID_R, grid_cols=GRID_C)
    ]
    
    print(f"\n--- COLLABORATION 1/2 ---")
    team_1_results = run_trials(env_collaboration, team_collaboration, "Collaboration Team", render_mode=render_mode_bool)
    
    # Render
    if RENDER_FLAG == 1:
        pygame.quit() 

    # Only Bot A
    
    env_solo = WarehouseRobot(grid_rows=GRID_R, grid_cols=GRID_C, fps=FPS)

    # Let B stay in same place
    class BotTypeA_Solo(BotTypeA):
        def get_action(self, my_index, all_robot_positions, target_pos, grid_rows, grid_cols):
            
            if my_index == 1:
                return RobotAction.DOWN
            
            my_pos = all_robot_positions[my_index]
            
            # keep original path
            if self.last_target_pos == target_pos and self.current_path:
                next_pos = self.current_path.pop(0)
                return self._pos_to_action(my_pos, next_pos)

            # let Bot B not become a block
            path = self.planner.find_path(my_pos, target_pos, blocked_pos=None)

            if path and len(path) > 1:
                self.current_path = path[1:]
                self.last_target_pos = target_pos
                next_pos = self.current_path.pop(0)
                return self._pos_to_action(my_pos, next_pos)
            else:
                return random.choice(list(RobotAction))

    # let B stay in same palce
    team_solo = [BotTypeA_Solo("P1 (Solo A*)", grid_rows=GRID_R, grid_cols=GRID_C), BotTypeA_Solo("P2 (Solo A*)", grid_rows=GRID_R, grid_cols=GRID_C)]
    
    print(f"\n--- SOLO 2/2 ---")
    team_2_results = run_trials(env_solo, team_solo, "Solo Bot A* (P2 Static)", render_mode=render_mode_bool)
    
    print("\n==================================================")
    if RENDER_FLAG == 0:
        print(f"🏆 {MAX_MISSIONS} RESULT")
        print("--------------------------------------------------")
        print(f"1. COLLABORATION TEAM ({team_collaboration[0].name} & {team_collaboration[1].name}):")
        print(f"   Average Steps: {team_1_results['avg_steps']:.2f}")
        print(f"   Exceed Limit: {team_1_results['timeouts']}")
        print(f"2. SOLO BOT ({team_solo[0].name} & P2 stop):")
        print(f"   Average Steps: {team_2_results['avg_steps']:.2f}")
        print(f"   Exceed Limit: {team_2_results['timeouts']}")
    else:
        print("RENDER MODE END")
    print("==================================================")
    
    pygame.quit()
    sys.exit()
    
def run_trials(env, team, name, render_mode=False):
    total_steps = 0
    timeouts = 0
    
    if render_mode:
        # render mode
        steps = run_mission(env, team, name, render_mode=render_mode) 
        total_steps = steps
        
    else:
        # experienment mode
        for i in range(MAX_MISSIONS):
            steps = run_mission(env, team, name, render_mode=render_mode) 
            total_steps += steps
            
            if steps == MAX_STEPS_PER_MISSION:
                timeouts += 1
                    
            if (i + 1) % 100 == 0 or i == MAX_MISSIONS - 1:
                avg = total_steps / (i + 1)
                print(f"  > Mission {i + 1}/{MAX_MISSIONS} | Avg Steps: {avg:.2f} | Timeouts: {timeouts}", end='\r')

        final_avg = total_steps / MAX_MISSIONS
        print(f"  > Mission {MAX_MISSIONS}/{MAX_MISSIONS} | Avg Steps: {final_avg:.2f} | Timeouts: {timeouts}")


    return {
        "total_steps": total_steps,
        "avg_steps": total_steps / MAX_MISSIONS if MAX_MISSIONS > 0 else 0,
        "timeouts": timeouts
    }

if __name__ == "__main__":
    run_experiment()