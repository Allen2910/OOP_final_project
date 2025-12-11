'''
Part 3 Demo: 雙機器人協作任務
展示兩個不同演算法的機器人如何共同完成目標
'''
from warehouse_robot import WarehouseRobot
from agents import BotTypeA, BotTypeB
import time

def run_collaboration():
    # 1. 初始化環境 (5x5 網格)
    env = WarehouseRobot(grid_rows=5, grid_cols=5, fps=4)
    
    # 2. 初始化兩個協作夥伴 (OOP 多型展示)
    # 這裡你可以取任何名字
    team = [
        BotTypeA("隊員 A (Algo 1)"),
        BotTypeB("隊員 B (Algo 2)")
    ]
    
    print(">>> 協作任務開始! <<<")
    print(f"Team: {team[0].name} & {team[1].name}")
    
    steps = 0
    mission_complete = False
    hero = None # 誰最後找到了包裹

    # 3. 任務迴圈
    while not mission_complete:
        env.render(f"Step: {steps}")
        
        # 讓隊伍裡的每個機器人輪流動一步
        for i, bot in enumerate(team):
            # 獲取該機器人的位置和目標位置
            my_pos = env.robot_positions[i]
            target_pos = env.target_pos
            
            # --- 多型 (Polymorphism) ---
            # 雖然都呼叫 get_action，但因為是不同的 Bot 類別，
            # 所以會執行你寫的兩種不同 ***algo***
            action = bot.get_action(my_pos, target_pos)
            
            # 執行動作
            # env.perform_action 會回傳 True 如果找到包裹
            found_package = env.perform_action(i, action)
            
            if found_package:
                hero = bot.name
                mission_complete = True
                break # 任務結束，跳出迴圈
        
        steps += 1
        
        # 防止跑太久當機
        if steps > 200:
            print("任務超時！")
            break

    # 4. 顯示結果
    env.render(f"Mission Complete! Found by {hero}")
    print(f"\n🏆 任務完成！")
    print(f"關鍵功臣: {hero}")
    print(f"總共花費步數: {steps}")
    
    time.sleep(3) # 停頓幾秒讓大家看結果

if __name__ == "__main__":
    run_collaboration()