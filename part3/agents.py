from abc import ABC, abstractmethod
import random
from warehouse_robot import RobotAction
import heapq

class AStarPlanner:
    def __init__(self, grid_rows, grid_cols):
        self.rows = grid_rows
        self.cols = grid_cols

    def heuristic(self, pos1, pos2):
        # Manhattan distance
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_path(self, start_pos, goal_pos, blocked_pos=None):

        if start_pos == goal_pos:
            return None

        priority_queue = [(0, 0, start_pos[0], start_pos[1])]
        g_cost = {tuple(start_pos): 0}
        came_from = {}
        
        blocked_tuple = tuple(blocked_pos) if blocked_pos else None
        
        while priority_queue:
            f_cost, g_current, r, c = heapq.heappop(priority_queue)
            current_pos = (r, c)

            if list(current_pos) == goal_pos:
                # rebuilt path
                path = []
                while current_pos in came_from:
                    path.append(list(current_pos))
                    current_pos = came_from[current_pos]
                path.append(list(start_pos))
                return path[::-1] 

            # go through 4 neighbor
            for dr, dc, action in [(-1, 0, RobotAction.UP), (1, 0, RobotAction.DOWN), (0, -1, RobotAction.LEFT), (0, 1, RobotAction.RIGHT)]:
                neighbor_r, neighbor_c = r + dr, c + dc
                neighbor_pos = (neighbor_r, neighbor_c)

                if 0 <= neighbor_r < self.rows and 0 <= neighbor_c < self.cols:
                    # avoid collapse
                    if blocked_tuple and neighbor_pos == blocked_tuple:
                        continue 
                        
                    new_g_cost = g_current + 1 

                    if new_g_cost < g_cost.get(neighbor_pos, float('inf')):
                        g_cost[neighbor_pos] = new_g_cost
                        f_cost = new_g_cost + self.heuristic(list(neighbor_pos), goal_pos)
                        heapq.heappush(priority_queue, (f_cost, new_g_cost, neighbor_r, neighbor_c))
                        came_from[neighbor_pos] = current_pos
        
        return None
    
class RobotAgent(ABC):
    def __init__(self, name, grid_rows=5, grid_cols=5):
        self.name = name
        self.planner = AStarPlanner(grid_rows, grid_cols)
        self.current_path = []
        self.last_target_pos = None
        
    def reset_agent(self):
        #clean cache
        self.current_path = []
        self.last_target_pos = None

    @abstractmethod
    def get_action(self, my_index, all_robot_positions, target_pos, grid_rows, grid_cols):
        pass
    def _pos_to_action(self, from_pos, to_pos):
        dr = to_pos[0] - from_pos[0]
        dc = to_pos[1] - from_pos[1]
        
        if dr == -1 and dc == 0: return RobotAction.UP
        if dr == 1 and dc == 0: return RobotAction.DOWN
        if dr == 0 and dc == 1: return RobotAction.RIGHT
        if dr == 0 and dc == -1: return RobotAction.LEFT
        
        # stay in same place
        return random.choice(list(RobotAction))

# Bot A: find kaggle directly
class BotTypeA(RobotAgent):
    def get_action(self, my_index, all_robot_positions, target_pos, grid_rows, grid_cols):
        my_pos = all_robot_positions[my_index]
        other_index = 1 - my_index
        other_pos = all_robot_positions[other_index]
        
        # keep original path
        if self.last_target_pos == target_pos and self.current_path:
            next_pos = self.current_path.pop(0)
            return self._pos_to_action(my_pos, next_pos)

        path = self.planner.find_path(my_pos, target_pos, blocked_pos=other_pos)

        if path and len(path) > 1:
            self.current_path = path[1:]
            self.last_target_pos = target_pos
            next_pos = self.current_path.pop(0)
            return self._pos_to_action(my_pos, next_pos)
        else:
            return random.choice(list(RobotAction))


# Bot B: approch A. if the distance to kaggle is less than 5 step, B will change to find kaggle
class BotTypeB(RobotAgent):

    def get_action(self, my_index, all_robot_positions, target_pos, grid_rows, grid_cols):
        my_pos = all_robot_positions[my_index]
        other_index = 1 - my_index
        bot_a_pos = all_robot_positions[other_index]
        
        dist_to_target = self.planner.heuristic(my_pos, target_pos)

        if dist_to_target < 5: 
            goal = target_pos
            mode_text = "ToPackage"
        else:
            goal = bot_a_pos
            mode_text = "ToBotA"

        # if mode change, then recalculate
        if self.last_target_pos == goal and self.current_path:
            next_pos = self.current_path.pop(0)
            return self._pos_to_action(my_pos, next_pos)
        
        # avoid A
        path = self.planner.find_path(my_pos, goal, blocked_pos=bot_a_pos)

        if path and len(path) > 1:
            self.current_path = path[1:]
            self.last_target_pos = goal
            next_pos = self.current_path.pop(0)
            return self._pos_to_action(my_pos, next_pos)
        else:
            return random.choice(list(RobotAction))