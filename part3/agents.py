'''
Agent Classes
這裡展示 OOP 架構：
1. 繼承 (Inheritance): 兩個機器人都繼承自 RobotAgent
2. 多型 (Polymorphism): 每個機器人用不同的演算法 (get_action)
'''
from abc import ABC, abstractmethod
import random
from warehouse_robot import RobotAction # 引用動作定義
import heapq

class AStarPlanner:
    def __init__(self, grid_rows, grid_cols):
        self.rows = grid_rows
        self.cols = grid_cols

    def heuristic(self, pos1, pos2):
        """曼哈頓距離 (Manhattan Distance) 作為啟發式函數"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_path(self, start_pos, goal_pos, blocked_pos=None):
        """
        使用 A* 演算法尋找路徑。
        blocked_pos: (可選) 路徑中要避開的位置 (例如：另一個機器人的位置)
        """
        if start_pos == goal_pos: return None # 已經到達

        priority_queue = [(0, 0, start_pos[0], start_pos[1])]
        g_cost = {tuple(start_pos): 0}
        came_from = {}
        
        # 將障礙物轉換為 tuple 以便查找
        blocked_tuple = tuple(blocked_pos) if blocked_pos else None
        
        while priority_queue:
            f_cost, g_current, r, c = heapq.heappop(priority_queue)
            current_pos = (r, c)

            if list(current_pos) == goal_pos:
                # 重建路徑
                path = []
                while current_pos in came_from:
                    path.append(list(current_pos))
                    current_pos = came_from[current_pos]
                path.append(list(start_pos))
                return path[::-1] 

            # 遍歷四個鄰居
            for dr, dc, action in [(-1, 0, RobotAction.UP), (1, 0, RobotAction.DOWN), (0, -1, RobotAction.LEFT), (0, 1, RobotAction.RIGHT)]:
                neighbor_r, neighbor_c = r + dr, c + dc
                neighbor_pos = (neighbor_r, neighbor_c)

                # 檢查邊界
                if 0 <= neighbor_r < self.rows and 0 <= neighbor_c < self.cols:
                    # 協作規則：不進入另一個機器人的格子 (避免碰撞/衝突)
                    if blocked_tuple and neighbor_pos == blocked_tuple:
                        continue 
                        
                    new_g_cost = g_current + 1 

                    if new_g_cost < g_cost.get(neighbor_pos, float('inf')):
                        g_cost[neighbor_pos] = new_g_cost
                        f_cost = new_g_cost + self.heuristic(list(neighbor_pos), goal_pos)
                        heapq.heappush(priority_queue, (f_cost, new_g_cost, neighbor_r, neighbor_c))
                        came_from[neighbor_pos] = current_pos
        
        return None # 找不到路徑
    
# === 基底類別 (父類別) ===
class RobotAgent(ABC):
    def __init__(self, name, grid_rows=5, grid_cols=5):
        self.name = name
        self.planner = AStarPlanner(grid_rows, grid_cols)
        self.current_path = []
        self.last_target_pos = None # 追蹤上一次的目標位置
        
    def reset_agent(self):
        """清除路徑緩存，在新任務開始時呼叫"""
        self.current_path = []
        self.last_target_pos = None

    @abstractmethod
    def get_action(self, my_index, all_robot_positions, target_pos, grid_rows, grid_cols):
        """
        抽象方法：子類別必須在這裡實作自己的演算法
        my_pos: [row, col]
        target_pos: [row, col]
        """
        pass
    def _pos_to_action(self, from_pos, to_pos):
        """將從一個位置到下一個位置的座標轉換為動作"""
        dr = to_pos[0] - from_pos[0]
        dc = to_pos[1] - from_pos[1]
        
        if dr == -1 and dc == 0: return RobotAction.UP
        if dr == 1 and dc == 0: return RobotAction.DOWN
        if dr == 0 and dc == 1: return RobotAction.RIGHT
        if dr == 0 and dc == -1: return RobotAction.LEFT
        
        # 停留在原地
        return random.choice(list(RobotAction))

# 機器人 A (主導導航者): A* 直衝包裹
class BotTypeA(RobotAgent):
    """
    主要導航者：始終使用 A* 尋找從自己位置到包裹的最短路徑。
    它避開另一個機器人當前的位置。
    """
    def get_action(self, my_index, all_robot_positions, target_pos, grid_rows, grid_cols):
        my_pos = all_robot_positions[my_index]
        other_index = 1 - my_index
        other_pos = all_robot_positions[other_index]
        
        # 1. 如果目標沒變，且路徑還沒走完，則繼續沿著規劃好的路徑走。
        if self.last_target_pos == target_pos and self.current_path:
            next_pos = self.current_path.pop(0)
            return self._pos_to_action(my_pos, next_pos)

        # 2. 目標改變或路徑走完，需要重新規劃
        # 重新計算 A* 路徑，並將另一個機器人的位置視為障礙
        path = self.planner.find_path(my_pos, target_pos, blocked_pos=other_pos)

        if path and len(path) > 1:
            self.current_path = path[1:] # 儲存路徑
            self.last_target_pos = target_pos # 記錄目標
            next_pos = self.current_path.pop(0)
            return self._pos_to_action(my_pos, next_pos)
        else:
            # 找不到路徑 (極少發生) 或已在目標點
            return random.choice(list(RobotAction))


# 機器人 B (輔助規劃者): A* 協作中繼
class BotTypeB(RobotAgent):
    """
    輔助規劃者：
    1. 計算包裹與自己的曼哈頓距離。
    2. 如果距離遠，則將「中繼點」設為 BotA 的位置，向 A 靠近。
    3. 如果距離近 (例如 < 5 步)，則直接轉向包裹。
    """
    def get_action(self, my_index, all_robot_positions, target_pos, grid_rows, grid_cols):
        my_pos = all_robot_positions[my_index]
        other_index = 1 - my_index
        bot_a_pos = all_robot_positions[other_index]
        
        # 計算到包裹的曼哈頓距離
        dist_to_target = self.planner.heuristic(my_pos, target_pos)

        # 決定目標點 (Target/Goal)
        if dist_to_target < 5: 
            # 模式 1: 包裹很近，直接衝向包裹
            goal = target_pos
            mode_text = "ToPackage"
        else:
            # 模式 2: 包裹很遠，衝向 Bot A 的位置進行匯合/支援
            goal = bot_a_pos
            mode_text = "ToBotA"

        # 1. 檢查是否需要重新規劃
        # 只要目標點變了 (從中繼點切換到包裹)，或者路徑走完，就要重新規劃。
        if self.last_target_pos == goal and self.current_path:
            next_pos = self.current_path.pop(0)
            return self._pos_to_action(my_pos, next_pos)
        
        # 2. 重新規劃路徑
        # 避開 Bot A 的位置
        path = self.planner.find_path(my_pos, goal, blocked_pos=bot_a_pos)

        if path and len(path) > 1:
            self.current_path = path[1:]
            self.last_target_pos = goal
            next_pos = self.current_path.pop(0)
            return self._pos_to_action(my_pos, next_pos)
        else:
            # 找不到路徑 (可能 BotA 就在旁邊，或已在目標點)
            return random.choice(list(RobotAction))