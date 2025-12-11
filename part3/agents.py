'''
Agent Classes
這裡展示 OOP 架構：
1. 繼承 (Inheritance): 兩個機器人都繼承自 RobotAgent
2. 多型 (Polymorphism): 每個機器人用不同的演算法 (get_action)
'''
from abc import ABC, abstractmethod
import random
from warehouse_robot import RobotAction # 引用動作定義

# === 基底類別 (父類別) ===
class RobotAgent(ABC):
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def get_action(self, my_pos, target_pos):
        """
        抽象方法：子類別必須在這裡實作自己的演算法
        my_pos: [row, col]
        target_pos: [row, col]
        """
        pass

# === 機器人 A (使用演算法 1) ===
class BotTypeA(RobotAgent):
    def get_action(self, my_pos, target_pos):
        # 獲取座標資訊
        row_diff = target_pos[0] - my_pos[0]
        col_diff = target_pos[1] - my_pos[1]
        
        # ---------------------------------------------------
        # ***algo***
        # 請在這裡實作第一種演算法 (例如：隨機亂走、先走橫的再走直的...)
        # ---------------------------------------------------
        
        # 這裡只是範例回傳，請替換成你的邏輯
        return random.choice(list(RobotAction))


# === 機器人 B (使用演算法 2) ===
class BotTypeB(RobotAgent):
    def get_action(self, my_pos, target_pos):
        # 獲取座標資訊
        row_diff = target_pos[0] - my_pos[0]
        col_diff = target_pos[1] - my_pos[1]

        # ---------------------------------------------------
        # ***algo***
        # 請在這裡實作第二種演算法 (例如：貪婪演算法、聰明路徑...)
        # ---------------------------------------------------

        # 這裡只是範例回傳，請替換成你的邏輯
        return random.choice(list(RobotAction))