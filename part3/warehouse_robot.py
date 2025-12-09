'''
Warehouse Robot Environment - Multi-Robot Collaboration Version
這個檔案負責管理：
1. 畫布 (Pygame)
2. 多個機器人的位置與移動規則
'''
import random
from enum import Enum
import pygame
import sys
from os import path

# 定義動作 (上下左右)
class RobotAction(Enum):
    LEFT=0
    DOWN=1
    RIGHT=2
    UP=3

# 定義地圖物件
class GridTile(Enum):
    _FLOOR=0
    ROBOT=1
    TARGET=2

class WarehouseRobot:
    def __init__(self, grid_rows=5, grid_cols=5, fps=10):
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.fps = fps
        self._init_pygame()
        self.reset()

    def _init_pygame(self):
        pygame.init()
        pygame.display.init()
        self.clock = pygame.time.Clock()
        self.action_font = pygame.font.SysFont("Arial", 20) 

        self.cell_height = 64
        self.cell_width = 64
        self.window_size = (self.cell_width * self.grid_cols, self.cell_height * self.grid_rows + 50)
        self.window_surface = pygame.display.set_mode(self.window_size) 

        # 載入圖片 (確保 sprites 資料夾存在且有這些圖)
        img_path = path.join(path.dirname(__file__), "sprites")
        try:
            # 載入並縮放圖片
            self.robot_img = pygame.transform.scale(pygame.image.load(path.join(img_path, "bot_blue.png")), (64, 64))
            self.floor_img = pygame.transform.scale(pygame.image.load(path.join(img_path, "floor.png")), (64, 64))
            self.goal_img = pygame.transform.scale(pygame.image.load(path.join(img_path, "package.png")), (64, 64))
        except Exception as e:
            print(f"圖片載入失敗，請檢查 sprites 資料夾: {e}")
            sys.exit()

    def reset(self):
        # 初始化兩個機器人的位置 (協作模式)
        # 機器人 0: 左上角 (0,0)
        # 機器人 1: 右下角 (最底, 最右)
        self.robot_positions = [
            [0, 0], 
            [self.grid_rows-1, self.grid_cols-1]
        ]

        # 隨機產生包裹位置
        while True:
            self.target_pos = [random.randint(0, self.grid_rows-1), random.randint(0, self.grid_cols-1)]
            # 確保包裹不會剛好生成在機器人腳下
            if self.target_pos not in self.robot_positions:
                break

    def perform_action(self, robot_index, action: RobotAction):
        """
        執行指定機器人的動作
        robot_index: 0 或 1 (代表哪一隻機器人)
        """
        current_pos = self.robot_positions[robot_index]
        new_pos = current_pos.copy()

        # 根據動作計算新位置
        if action == RobotAction.LEFT and current_pos[1] > 0:
            new_pos[1] -= 1
        elif action == RobotAction.RIGHT and current_pos[1] < self.grid_cols - 1:
            new_pos[1] += 1
        elif action == RobotAction.UP and current_pos[0] > 0:
            new_pos[0] -= 1
        elif action == RobotAction.DOWN and current_pos[0] < self.grid_rows - 1:
            new_pos[0] += 1
        
        # 更新該機器人的位置
        self.robot_positions[robot_index] = new_pos

        # 檢查是否碰到包裹 (任務完成)
        if new_pos == self.target_pos:
            return True 
        return False

    def render(self, info_text=""):
        self._process_events()
        self.window_surface.fill((255, 255, 255))

        # 1. 畫地板和包裹
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                pos = (c * self.cell_width, r * self.cell_height)
                self.window_surface.blit(self.floor_img, pos)
                if [r, c] == self.target_pos:
                    self.window_surface.blit(self.goal_img, pos)

        # 2. 畫所有機器人
        for i, pos in enumerate(self.robot_positions):
            pixel_pos = (pos[1] * self.cell_width, pos[0] * self.cell_height)
            self.window_surface.blit(self.robot_img, pixel_pos)
            
            # 標記 P1, P2 以示區別
            label = self.action_font.render(f"P{i+1}", True, (255, 0, 0)) # 紅色字
            self.window_surface.blit(label, pixel_pos)

        # 3. 顯示底部資訊
        text_surf = self.action_font.render(info_text, True, (0, 0, 0))
        self.window_surface.blit(text_surf, (10, self.window_size[1] - 40))

        pygame.display.update()
        self.clock.tick(self.fps)

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()