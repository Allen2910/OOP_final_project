# part3/src/agents.py
from .base_agent import BaseWarehouseAgent, state_to_index
import numpy as np

# 派生類別 1: Q-Learning 代理器 (Off-Policy)
class QLearningAgent(BaseWarehouseAgent):
    """
    Q-Learning 代理器 (Off-Policy)，繼承 BaseWarehouseAgent。
    學習的是最優策略 Q* (使用 max(Q(S', a')))。
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化 Q-Table: Shape 為 (grid_rows, grid_cols, grid_rows, grid_cols, action_size)
        q_table_shape = self._state_shape + (self._action_size,)
        self._q_table = np.zeros(q_table_shape)

    # 覆寫 choose_action (探索策略)
    def choose_action(self, state: np.ndarray) -> int:
        # Epsilon-Greedy 策略
        if np.random.rand() < self._epsilon:
            return np.random.randint(self._action_size)
        return np.argmax(self._q_table[state_to_index(state)])

    # 覆寫 learn (Polymorphism 核心: Q-Learning 更新公式)
    def learn(self, state, action, reward, next_state, next_action=None):
        """
        Q-Learning: 使用 S' 狀態的最大 Q 值 (max(Q(S', a')))。
        """
        state_idx = state_to_index(state)
        next_state_idx = state_to_index(next_state)
        
        old_value = self._q_table[state_idx + (action,)]
        
        # 關鍵差異: 尋找下一狀態的最大 Q 值 (max(Q(S', a')) )
        next_max = np.max(self._q_table[next_state_idx])
        
        # Q-Learning 更新公式
        target = reward + self._gamma * next_max
        new_value = old_value + self._lr * (target - old_value)
        
        self._q_table[state_idx + (action,)] = new_value


# 派生類別 2: SARSA 代理器 (On-Policy)
class SARSAAgent(BaseWarehouseAgent):
    """
    SARSA 代理器 (On-Policy)，繼承 BaseWarehouseAgent。
    學習的是當前策略下的 Q 值 Q^pi (使用 Q(S', A'))。
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化 Q-Table
        q_table_shape = self._state_shape + (self._action_size,)
        self._q_table = np.zeros(q_table_shape)

    # 覆寫 choose_action (策略與探索策略相同)
    def choose_action(self, state: np.ndarray) -> int:
        # Epsilon-Greedy 策略 (與 QL 相同)
        if np.random.rand() < self._epsilon:
            return np.random.randint(self._action_size)
        return np.argmax(self._q_table[state_to_index(state)])

    # 覆寫 learn (Polymorphism 核心: SARSA 更新公式)
    def learn(self, state, action, reward, next_state, next_action):
        """
        SARSA: 使用 S' 狀態和**已選擇**的下一個動作 (Q(S', A'))。
        """
        # SARSA 在 learn 時必須有 next_action
        if next_action is None: return
            
        state_idx = state_to_index(state)
        next_state_idx = state_to_index(next_state)
        
        old_value = self._q_table[state_idx + (action,)]
        
        # 關鍵差異: 使用傳入的 next_action 來獲取 Q(S', A')
        next_q_value = self._q_table[next_state_idx + (next_action,)]
        
        # SARSA 更新公式
        target = reward + self._gamma * next_q_value
        new_value = old_value + self._lr * (target - old_value)
        
        self._q_table[state_idx + (action,)] = new_value