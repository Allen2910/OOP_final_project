'''
Part 3 Demo: 雙機器人協作任務
展示兩個不同演算法的機器人如何共同完成目標
'''
from warehouse_robot import WarehouseRobot, RobotAction
from agents import BotTypeA, BotTypeB
import time
import random
import sys
import pygame

GRID_R, GRID_C = 10, 10
FPS = 4
MAX_MISSIONS = 1000 # 包裹數
MAX_STEPS_PER_MISSION = 500 # 單次步數上限

def run_mission(env: WarehouseRobot, team: list, render_mode=True):
    """
    執行單次尋找包裹的任務
    :param env: 機器人環境
    :param team: 機器人列表 (e.g., [BotA, BotB] 或 [BotA])
    :param render_mode: 是否渲染畫面
    :return: 任務步數 (int)
    """
    
    # 確保環境和所有機器人都重置
    env.reset()
    for bot in team:
        bot.reset_agent() # 清除機器人內部的路徑緩存
    
    steps = 0
    mission_complete = False
    hero = None
    
    # 任務迴圈
    while not mission_complete:
        
        all_robot_positions = env.robot_positions 
        target_pos = env.target_pos
        
        # 讓隊伍裡的每個機器人輪流動一步
        for i, bot in enumerate(team):
            
            # **【關鍵】**：傳遞所有必要資訊給 get_action
            action = bot.get_action(
                my_index=i, 
                all_robot_positions=all_robot_positions, 
                target_pos=target_pos,
                grid_rows=GRID_R, 
                grid_cols=GRID_C
            )
            
            # 執行動作
            found_package = env.perform_action(i, action)
            
            if render_mode:
                # 渲染資訊更新
                info_text = f"Step: {steps + 1}. {bot.name}: {action.name}"
                env.render(info_text)
            
            if found_package:
                hero = bot.name
                mission_complete = True
                break # 任務結束，跳出 for 迴圈
        
        steps += 1
        
        # 防止跑太久當機或超時
        if steps > MAX_STEPS_PER_MISSION:
            print(f"任務超時 ({team[0].name} 組): {steps} 步！")
            mission_complete = True
            steps = MAX_STEPS_PER_MISSION # 紀錄超時的懲罰步數
            if render_mode:
                env.render("Mission Timeout!")
            break

    # if render_mode:
    #     env.render(f"Mission Complete! Found by {hero} in {steps} steps.")
    
    return steps

def run_experiment():
    # 1. 初始化環境
    render_fps = 0 # 設為 0 不渲染
    env = WarehouseRobot(grid_rows=GRID_R, grid_cols=GRID_C, fps=render_fps)
    
    # 2. 定義實驗組 (兩個組別)
    
    # 實驗組 1: 雙機器人協作 (BotA + BotB)
    team_collaboration = [
        BotTypeA("P1 (A* main)", grid_rows=GRID_R, grid_cols=GRID_C),
        BotTypeB("P2 (A* supporter)", grid_rows=GRID_R, grid_cols=GRID_C)
    ]
    
    print("--------------------------------------------------")
    print(f"Starting {MAX_MISSIONS} Missions Experiment...")
    print("--------------------------------------------------")
    
    # 實驗 1: 雙機器人協作組
    team_1_results = run_trials(env, team_collaboration, "Collaboration Team", render_on_fail=False)

    pygame.quit() 
    
    # 新建一個 BotA 實例給單機組
    team_solo = [BotTypeA("P1 (Solo A*)", grid_rows=GRID_R, grid_cols=GRID_C)]
    
    # 重新初始化環境 (因為上面 quit 了)
    env_solo = WarehouseRobot(grid_rows=GRID_R, grid_cols=GRID_C, fps=render_fps)
    env_solo = WarehouseRobot(grid_rows=GRID_R, grid_cols=GRID_C, fps=render_fps)
    
    # 重新創建單機組，它的 BotTypeA 必須被修改
    # 創建一個新的 class 來模擬單機行為
    class BotTypeA_Solo(BotTypeA):
        """單機版 BotA，不將其他機器人設為障礙"""
        def get_action(self, my_index, all_robot_positions, target_pos, grid_rows, grid_cols):
            my_pos = all_robot_positions[my_index]
            
            # 1. 如果目標沒變，且路徑還沒走完，則繼續沿著規劃好的路徑走。
            if self.last_target_pos == target_pos and self.current_path:
                next_pos = self.current_path.pop(0)
                return self._pos_to_action(my_pos, next_pos)

            # 2. 目標改變或路徑走完，需要重新規劃
            # 重新計算 A* 路徑，不將另一個機器人的位置視為障礙 (blocked_pos=None)
            path = self.planner.find_path(my_pos, target_pos, blocked_pos=None) # <-- 關鍵差異

            if path and len(path) > 1:
                self.current_path = path[1:] # 儲存路徑
                self.last_target_pos = target_pos # 記錄目標
                next_pos = self.current_path.pop(0)
                return self._pos_to_action(my_pos, next_pos)
            else:
                return random.choice(list(RobotAction))

    team_solo = [BotTypeA_Solo("P1 (Solo A*)", grid_rows=GRID_R, grid_cols=GRID_C), BotTypeA_Solo("P2 (Solo A*)", grid_rows=GRID_R, grid_cols=GRID_C)]
    
    # 運行實驗
    team_2_results = run_trials(env_solo, team_solo, "Solo Bot A* (Ignored Collision)", render_on_fail=False)


    print("\n==================================================")
    print(f"🏆 1000 輪倉庫尋物任務結果")
    print("==================================================")
    
    print(f"1. 雙機器人協作組 ({team_collaboration[0].name} & {team_collaboration[1].name}):")
    print(f"   總步數: {team_1_results['total_steps']}")
    print(f"   平均步數: {team_1_results['avg_steps']:.2f}")
    print(f"   超時任務數: {team_1_results['timeouts']}")
    
    print("-" * 50)
    
    print(f"2. 單機器人對照組 ({team_solo[0].name}):")
    print(f"   總步數: {team_2_results['total_steps']}")
    print(f"   平均步數: {team_2_results['avg_steps']:.2f}")
    print(f"   超時任務數: {team_2_results['timeouts']}")
    print("==================================================")
    
    # 關閉視窗
    pygame.quit()
    sys.exit()
    
def run_trials(env, team, name, render_on_fail=False):
    """運行多輪試驗並計算統計數據"""
    total_steps = 0
    timeouts = 0
    
    print(f"\n--- 正在運行 {name} ({MAX_MISSIONS} 次) ---")
    
    for i in range(MAX_MISSIONS):
        steps = run_mission(env, team, render_mode=False) # 預設不渲染
        total_steps += steps
        
        if steps == MAX_STEPS_PER_MISSION:
            timeouts += 1
            if render_on_fail:
                env.fps = 4
                run_mission(env, team, render_mode=True) 
                env.fps = 0
                
        # 進度條
        if (i + 1) % 100 == 0 or i == MAX_MISSIONS - 1:
            avg = total_steps / (i + 1)
            print(f"  > Mission {i + 1}/{MAX_MISSIONS} | Avg Steps: {avg:.2f} | Timeouts: {timeouts}", end='\r')

    print(f"  > Mission {MAX_MISSIONS}/{MAX_MISSIONS} | Avg Steps: {total_steps / MAX_MISSIONS:.2f} | Timeouts: {timeouts}")
    
    return {
        "total_steps": total_steps,
        "avg_steps": total_steps / MAX_MISSIONS,
        "timeouts": timeouts
    }

if __name__ == "__main__":
    run_experiment()