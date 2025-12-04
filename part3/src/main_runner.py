# part3/src/main_runner.py
import gymnasium as gym
import numpy as np
import os
import sys

# 為了確保在 part3/src 中可以找到 part3/ 的模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 導入環境註冊檔和 Agent 結構
import oop_project_env 
from src.base_agent import BaseWarehouseAgent
from src.agents import QLearningAgent, SARSAAgent


def run_single_episode(env, agent: BaseWarehouseAgent):
    """執行單次回合，返回總獎勵。"""
    state, _ = env.reset()
    done = False
    total_reward = 0
    
    # 第一次動作選擇：所有 Agent 都需要第一個動作
    action = agent.choose_action(state)

    while not done:
        
        # SARSA 的策略：使用 choose_action 選擇 A'
        if isinstance(agent, SARSAAgent):
            next_action = agent.choose_action(state)
        else:
            # Q-Learning (Off-policy) 不需要在這裡選擇 A'
            next_action = None

        # 環境執行動作
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        total_reward += reward
        
        # Polymorphism 核心：呼叫 learn() 方法
        # 儘管 QL 和 SARSA 的 learn 邏輯不同，但函式呼叫保持通用。
        agent.learn(state, action, reward, next_state, next_action)
        
        # 狀態和動作轉移
        state = next_state
        
        if isinstance(agent, SARSAAgent):
            # SARSA (On-policy): S <- S', A <- A'
            action = next_action 
        else:
            # Q-Learning (Off-policy): 在新狀態 S' 上使用策略選擇新的動作 A'
            action = agent.choose_action(state) 
            
    return total_reward

def run_experiment(agent: BaseWarehouseAgent, env, episodes=100, save_dir="part3/models"):
    """使用多型函式訓練 Agent。"""
    agent_name = agent.__class__.__name__
    print(f"\n--- Starting experiment with {agent_name} (Episodes: {episodes}) ---")
    
    # 確保 models 資料夾存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for episode in range(1, episodes + 1):
        total_reward = run_single_episode(env, agent)
        
        # Epsilon 衰減 (控制探索與利用的平衡)
        current_epsilon = agent.decay_epsilon()
        
        if episode % 10 == 0 or episode == episodes:
             print(f"Episode {episode}: Total Reward = {total_reward}, Epsilon = {current_epsilon:.4f}")

    # 示範 Overloading：使用不同的參數呼叫相同的 save_model 函式
    agent.save_model(f"../models/{agent_name}_q_table.pkl")
    agent.save_model(f"../models/{agent_name}_config.pkl", include_q_table=False)


if __name__ == "__main__":
    # 1. 初始化環境
    # grid_rows=4, grid_cols=5 (共 20 格)
    ENV_ID = 'warehouse-robot-v0'
    EPISODES = 50 
    
    print(f"Initializing Environment: {ENV_ID}")
    env = gym.make(ENV_ID, render_mode=None) # 建議訓練時關閉 render_mode

    # 獲取環境參數
    action_size = env.action_space.n 
    # 觀察空間的上限值 + 1，作為 Q-Table 的維度 (4x5x4x5)
    state_high_limits = env.observation_space.high + 1 
    
    # 2. 初始化 Agent 參數
    common_params = {
        'action_space_size': action_size,
        'state_space_shape': state_high_limits,
        'learning_rate': 0.1,
        'discount_factor': 0.9
    }

    # 實例化兩個不同的 Agent 類別
    q_agent = QLearningAgent(**common_params)
    sarsa_agent = SARSAAgent(**common_params)

    # 3. 運行實驗 (展示多型性)
    # 使用相同的 run_experiment 函式，但由於 Agent 實作不同，訓練邏輯完全不同
    run_experiment(q_agent, env, episodes=EPISODES)
    run_experiment(sarsa_agent, env, episodes=EPISODES)
    
    env.close()