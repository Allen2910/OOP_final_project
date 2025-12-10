'''
Part 3 Demo: 雙機器人協作任務
展示兩個不同演算法的機器人如何共同完成目標
'''
from warehouse_robot import WarehouseRobot
from agents import BotTypeA, BotTypeB
import time

GRID_R, GRID_C = 10, 10
FPS = 4

def run_collaboration():
    # 1. 初始化環境 (5x5 網格)
    env = WarehouseRobot(grid_rows=GRID_R, grid_cols=GRID_C, fps=FPS)
    
    # 2. 初始化兩個協作夥伴 (OOP 多型展示)
    # 這裡你可以取任何名字
    team = [
        BotTypeA("P1 (A* main)", grid_rows=GRID_R, grid_cols=GRID_C),
        # BotTypeB 擔任輔助者，從 (R-1, C-1) 開始
        BotTypeB("P2 (A* supporter)", grid_rows=GRID_R, grid_cols=GRID_C)
    ]
    
    print(">>> 協作任務開始! <<<")
    print(f"Team: {team[0].name} & {team[1].name}")
    
    steps = 0
    mission_complete = False
    hero = None # 誰最後找到了包裹

    env.reset()

    # 3. 任務迴圈
    while not mission_complete:
        
        # 獲取一次所有機器人的位置和目標位置 (用於協作判斷)
        all_robot_positions = env.robot_positions 
        target_pos = env.target_pos
        
        # 讓隊伍裡的每個機器人輪流動一步
        for i, bot in enumerate(team):
            
            # **【關鍵修改】**：傳遞所有必要資訊給 get_action
            action = bot.get_action(
                my_index=i, 
                all_robot_positions=all_robot_positions, 
                target_pos=target_pos,
                grid_rows=GRID_R, # 雖然 BotTypeB 內部有 planner，傳遞 grid_rows/cols 確保魯棒性
                grid_cols=GRID_C
            )
            
            # 執行動作
            found_package = env.perform_action(i, action)
            
            # 渲染資訊更新
            info_text = f"Step: {steps + 1}. P{i+1}: {action.name}"
            env.render(info_text)
            
            if found_package:
                hero = bot.name
                mission_complete = True
                break # 任務結束，跳出 for 迴圈
        
        steps += 1
        
        # 防止跑太久當機
        if steps > 200:
            print("任務超時！(可能陷入迴圈或路徑太長)")
            mission_complete = True
            hero = "None (Timeout)"
            env.render("Mission Timeout!")
            break

    # 4. 顯示結果
    env.render(f"Mission Complete! Found by {hero}")
    print(f"\n🏆 任務完成！")
    print(f"關鍵功臣: {hero}")
    print(f"總共花費步數: {steps}")
    
    # 最終渲染
    env.render(f"Mission Complete! Found by {hero} in {steps} steps.")
    time.sleep(3)

if __name__ == "__main__":
    run_collaboration()