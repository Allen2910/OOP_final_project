# part3/src/base_agent.py
from abc import ABC, abstractmethod
import numpy as np
import pickle

class BaseWarehouseAgent(ABC):
    """
    倉庫機器人代理器的基底抽象類別。
    - 定義所有 Agent 必須具備的介面 (Polymorphism)。
    - 示範 Encapsulation 和 Overloading。
    """
    
    def __init__(self, action_space_size, state_space_shape, learning_rate=0.1, discount_factor=0.99):
        # 示範 Encapsulation (封裝)：使用保護屬性 (單底線) 儲存內部狀態
        self._action_size = action_space_size
        self._state_shape = tuple(state_space_shape)
        self._lr = learning_rate       # 學習率
        self._gamma = discount_factor  # 折扣因子
        self._epsilon = 1.0            # 探索率 (會隨著訓練衰減)
        self._q_table = None           # 留待子類別初始化

    @abstractmethod
    def choose_action(self, state: np.ndarray) -> int:
        """核心方法：根據當前狀態選擇動作。所有子類別必須實作。"""
        pass

    @abstractmethod
    def learn(self, state, action, reward, next_state, next_action=None):
        """核心方法：根據經驗更新學習模型。所有子類別必須實作。"""
        pass

    def decay_epsilon(self, decay_rate=0.995, min_epsilon=0.01):
        """公共方法：衰減探索率，用於訓練過程的策略調整。"""
        self._epsilon = max(min_epsilon, self._epsilon * decay_rate)
        return self._epsilon

    # 示範 Polymorphism/Overloading (多載/預設參數)：根據參數執行不同行為
    def save_model(self, file_path, include_q_table=True):
        """
        將 Agent 狀態儲存到指定路徑。
        - include_q_table=True: 儲存 Q-Table 和所有配置。
        - include_q_table=False: 只儲存配置 (Epsilon, LR 等)。
        """
        data = {
            'lr': self._lr, 
            'gamma': self._gamma,
            'epsilon': self._epsilon
        }
        
        if include_q_table and self._q_table is not None:
            data['q_table'] = self._q_table
            message = "Model (including Q-Table) saved."
        else:
            message = "Basic config (without Q-Table) saved."
            
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"[{self.__class__.__name__}] {message} Path: {file_path}")
        except Exception as e:
            print(f"[{self.__class__.__name__}] Save failed: {e}")

# 輔助函式：將環境的狀態 (pos_r, pos_c, target_r, target_c) 轉換為 Q-Table 的索引 tuple
def state_to_index(state):
    """將 Numpy 狀態陣列轉換為 Q-Table 的 tuple 索引。"""
    # 確保狀態值是整數，作為索引
    return tuple(state.astype(int))