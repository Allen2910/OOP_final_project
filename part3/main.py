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

# --- 核心設定 (通過布林值控制渲染) ---
RENDER_FLAG = 1 # 0: 不渲染(數據模式), 1: 渲染(視覺模式)

# 根據 RENDER_FLAG 調整實驗參數
GRID_R, GRID_C = 10, 10

if RENDER_FLAG == 1:
    print("--- 模式: 視覺化 (Render ON) ---")
    FPS = 4
    MAX_MISSIONS = 1
    MAX_STEPS_PER_MISSION = 500 # 視覺模式給予更多步數容錯
else:
    print("--- 模式: 數據採集 (Render OFF) ---")
    FPS = 0
    MAX_MISSIONS = 100
    MAX_STEPS_PER_MISSION = 300

def run_mission(env: WarehouseRobot, team: list, team_name: str, render_mode):
    """
    執行單次尋找包裹的任務
    【注意】 render_mode 參數不再有預設值，解決了 TypeError 錯誤。
    """
    
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
            
            # 執行動作
            found_package = env.perform_action(i, action)
            
            if render_mode:
                # 渲染資訊更新
                info_text = f"[{team_name}] Step: {steps + 1}. {bot.name}: {action.name}"
                env.render(info_text)
            
            if found_package:
                hero = bot.name
                mission_complete = True
                break
        
        steps += 1
        
        if steps > MAX_STEPS_PER_MISSION:
            # print(f"任務超時 ({team_name}): {steps} 步！") # 數據模式下避免頻繁輸出
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
    
    # 1. 初始化環境
    render_mode_bool = (RENDER_FLAG == 1)
    
    print("==================================================")
    if RENDER_FLAG == 1:
        print("🏆 機器人尋包任務視覺化開始! (共 2 輪)")
    else:
        print(f"🏆 數據採集開始! (共 {MAX_MISSIONS} 輪)")
    print("==================================================")
    
    # --------------------------------------------------
    # 實驗 1: 雙機器人協作組 (BotA + BotB)
    # --------------------------------------------------
    env_collaboration = WarehouseRobot(grid_rows=GRID_R, grid_cols=GRID_C, fps=FPS)
    team_collaboration = [
        BotTypeA("P1 (A* main)", grid_rows=GRID_R, grid_cols=GRID_C),
        BotTypeB("P2 (A* supporter)", grid_rows=GRID_R, grid_cols=GRID_C)
    ]
    
    print(f"\n--- 運行 1/2: 雙機器人協作組 ---")
    team_1_results = run_trials(env_collaboration, team_collaboration, "Collaboration Team", render_mode=render_mode_bool)
    
    # 如果有渲染，需要關閉視窗
    if RENDER_FLAG == 1:
        pygame.quit() 
    
    # --------------------------------------------------
    # 實驗 2: 單機器人對照組 (Bot A Solo - P2 靜止)
    # --------------------------------------------------
    
    env_solo = WarehouseRobot(grid_rows=GRID_R, grid_cols=GRID_C, fps=FPS)

    # 創建一個忽略第二個機器人位置的 BotA 實例 (單機對照組)
    class BotTypeA_Solo(BotTypeA):
        """單機版 BotA，不將其他機器人設為障礙，P2 (index 1) 保持原地不動。"""
        def get_action(self, my_index, all_robot_positions, target_pos, grid_rows, grid_cols):
            
            # --- 【關鍵修復】: 如果是 P2 (index 1)，強制返回 DOWN 動作 ---
            if my_index == 1:
                # P2 初始在底部邊界 (R-1)，嘗試向下移動會被環境的邊界檢查阻止，從而原地不動。
                return RobotAction.DOWN
            # --- 【修復邏輯結束】 ---
            
            my_pos = all_robot_positions[my_index] # P1 的邏輯繼續
            
            # 1. 如果目標沒變，且路徑還沒走完，則繼續沿著規劃好的路徑走。
            if self.last_target_pos == target_pos and self.current_path:
                next_pos = self.current_path.pop(0)
                return self._pos_to_action(my_pos, next_pos)

            # 2. 重新規劃路徑，不將另一個機器人的位置視為障礙 (blocked_pos=None)
            path = self.planner.find_path(my_pos, target_pos, blocked_pos=None)

            if path and len(path) > 1:
                self.current_path = path[1:]
                self.last_target_pos = target_pos
                next_pos = self.current_path.pop(0)
                return self._pos_to_action(my_pos, next_pos)
            else:
                return random.choice(list(RobotAction))

    # P1 和 P2 都是 BotTypeA_Solo，但 P2 會被內建邏輯鎖定在右下角
    team_solo = [BotTypeA_Solo("P1 (Solo A*)", grid_rows=GRID_R, grid_cols=GRID_C), BotTypeA_Solo("P2 (Solo A*)", grid_rows=GRID_R, grid_cols=GRID_C)]
    
    print(f"\n--- 運行 2/2: 單機器人對照組 ---")
    team_2_results = run_trials(env_solo, team_solo, "Solo Bot A* (P2 Static)", render_mode=render_mode_bool)
    
    print("\n==================================================")
    if RENDER_FLAG == 0:
        print(f"🏆 {MAX_MISSIONS} 輪倉庫尋物任務結果")
        print("--------------------------------------------------")
        print(f"1. 雙機器人協作組 ({team_collaboration[0].name} & {team_collaboration[1].name}):")
        print(f"   平均步數: {team_1_results['avg_steps']:.2f}")
        print(f"   超時任務數: {team_1_results['timeouts']}")
        print(f"2. 單機器人對照組 ({team_solo[0].name} & P2 靜止):")
        print(f"   平均步數: {team_2_results['avg_steps']:.2f}")
        print(f"   超時任務數: {team_2_results['timeouts']}")
    else:
        print("視覺化任務運行完畢。")
    print("==================================================")
    
    # 關閉視窗
    pygame.quit()
    sys.exit()
    
def run_trials(env, team, name, render_mode=False):
    """運行多輪試驗並計算統計數據"""
    total_steps = 0
    timeouts = 0
    
    if render_mode:
        # 視覺模式只運行一次
        steps = run_mission(env, team, name, render_mode=render_mode) 
        total_steps = steps
        
    else:
        # 數據模式運行 MAX_MISSIONS 次
        for i in range(MAX_MISSIONS):
            steps = run_mission(env, team, name, render_mode=render_mode) 
            total_steps += steps
            
            if steps == MAX_STEPS_PER_MISSION:
                timeouts += 1
                    
            # 進度條/狀態更新
            if (i + 1) % 100 == 0 or i == MAX_MISSIONS - 1:
                avg = total_steps / (i + 1)
                print(f"  > Mission {i + 1}/{MAX_MISSIONS} | Avg Steps: {avg:.2f} | Timeouts: {timeouts}", end='\r')

        final_avg = total_steps / MAX_MISSIONS
        print(f"  > Mission {MAX_MISSIONS}/{MAX_MISSIONS} | Avg Steps: {final_avg:.2f} | Timeouts: {timeouts}")


    # 返回結果
    return {
        "total_steps": total_steps,
        "avg_steps": total_steps / MAX_MISSIONS if MAX_MISSIONS > 0 else 0,
        "timeouts": timeouts
    }

if __name__ == "__main__":
    run_experiment()