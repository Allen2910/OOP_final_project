import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
import pickle


def print_success_rate(rewards_per_episode):
    """Calculate and print the success rate of the agent."""
    total_episodes = len(rewards_per_episode)
    success_count = np.sum(rewards_per_episode)
    success_rate = (success_count / total_episodes) * 100
    print(f"✅ Success Rate: {success_rate:.2f}% ({int(success_count)} / {total_episodes} episodes)")
    return success_rate

def run(episodes, is_training=True, render=False):

    env = gym.make('FrozenLake-v1', map_name="8x8", is_slippery=True, render_mode='human' if render else None)

    if(is_training):
        q = np.zeros((env.observation_space.n, env.action_space.n)) # init a 64 x 4 array
    else:
        f = open('frozen_lake8x8.pkl', 'rb')
        q = pickle.load(f)
        f.close()

    learning_rate_a = 0.9 # alpha or learning rate
    discount_factor_g = 0.9 # gamma or discount rate. Near 0: more weight/reward placed on immediate state. Near 1: more on future state.
    epsilon = 1         # 1 = 100% random actions
    epsilon_decay_rate = 0.0001        # epsilon decay rate. 1/0.0001 = 10,000
    rng = np.random.default_rng()   # random number generator

    rewards_per_episode = np.zeros(episodes)

    for i in range(episodes):
        state = env.reset()[0]  # states: 0 to 63, 0=top left corner,63=bottom right corner
        terminated = False      # True when fall in hole or reached goal
        truncated = False       # True when actions > 200

        while(not terminated and not truncated):
            if is_training and rng.random() < epsilon:
                action = env.action_space.sample() # actions: 0=left,1=down,2=right,3=up
            else:
                action = np.argmax(q[state,:])

            new_state,reward,terminated,truncated,_ = env.step(action)

            if is_training:
                q[state,action] = q[state,action] + learning_rate_a * (
                    reward + discount_factor_g * np.max(q[new_state,:]) - q[state,action]
                )

            state = new_state

        epsilon = max(epsilon - epsilon_decay_rate, 0)

        if(epsilon==0):
            learning_rate_a = 0.0001

        if reward == 1:
            rewards_per_episode[i] = 1

    env.close()

    sum_rewards = np.zeros(episodes)
    for t in range(episodes):
        sum_rewards[t] = np.sum(rewards_per_episode[max(0, t-100):(t+1)])
    plt.plot(sum_rewards)
    plt.savefig('frozen_lake8x8.png')
    
    if is_training == False:
        print(print_success_rate(rewards_per_episode))

    if is_training:
        f = open("frozen_lake8x8.pkl","wb")
        pickle.dump(q, f)
        f.close()

import numpy as np

def value_iteration(env, gamma=0.99, theta=1e-8):
    """
    Value Iteration: returns optimal policy.
    """
    env_unwrapped = env.unwrapped
    n_states = env_unwrapped.observation_space.n
    n_actions = env_unwrapped.action_space.n
    P = env_unwrapped.P

    V = np.zeros(n_states)

    while True:
        delta = 0
        for s in range(n_states):
            q_values = np.zeros(n_actions)
            for a in range(n_actions):
                for prob, next_s, reward, done in P[s][a]:
                    q_values[a] += prob * (reward + gamma * V[next_s])

            new_v = np.max(q_values)
            delta = max(delta, abs(V[s] - new_v))
            V[s] = new_v

        if delta < theta:
            break

    # extract optimal policy
    policy = np.zeros(n_states, dtype=int)
    for s in range(n_states):
        q_values = np.zeros(n_actions)
        for a in range(n_actions):
            for prob, next_s, reward, done in P[s][a]:
                q_values[a] += prob * (reward + gamma * V[next_s])
        policy[s] = np.argmax(q_values)

    return policy

def run_value_iteration(episodes=5000, render=False, load=False):
    env = gym.make('FrozenLake-v1', map_name="8x8", is_slippery=True, render_mode='human' if render else None)

    # ---------------- load or compute policy ----------------
    if load:
        with open("frozen_lake_vi_policy.pkl", "rb") as f:
            policy = pickle.load(f)
    else:
        policy = value_iteration(env)
        with open("frozen_lake_vi_policy.pkl", "wb") as f:
            pickle.dump(policy, f)

    # ---------------- evaluation ----------------
    rewards_per_episode = np.zeros(episodes)

    for ep in range(episodes):
        state, _ = env.reset()
        terminated = False
        truncated = False

        while not (terminated or truncated):
            action = policy[state]
            state, reward, terminated, truncated, _ = env.step(action)

        rewards_per_episode[ep] = reward

    # ---------------- print results ----------------
    print_success_rate(rewards_per_episode)

    env.close()



def run_sarsa(episodes, is_training=True, render=False):

    env = gym.make('FrozenLake-v1', map_name="8x8", is_slippery=True,
                   render_mode='human' if render else None)

    # ----------- 初始化 Q-table 或讀取 -----------
    if is_training:
        q = np.zeros((env.observation_space.n, env.action_space.n))
    else:
        with open('frozen_lake8x8_sarsa.pkl', 'rb') as f:
            q = pickle.load(f)

    # ---------------- hyperparameters ----------------
    alpha = 0.9
    gamma = 0.9
    epsilon = 1
    epsilon_decay_rate = 0.0001

    rng = np.random.default_rng()
    rewards_per_episode = np.zeros(episodes)

    # ------------------- SARSA 主迴圈 -------------------
    for ep in range(episodes):

        state, _ = env.reset()
        terminated = False
        truncated = False

        # 依 SARSA: 第一個 action 使用 ε-greedy
        if is_training and rng.random() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(q[state])

        while not (terminated or truncated):

            new_state, reward, terminated, truncated, _ = env.step(action)

            # ---------------- SARSA 更新 ----------------
            if is_training:

                # next action a' 採用 ε-greedy
                if rng.random() < epsilon:
                    next_action = env.action_space.sample()
                else:
                    next_action = np.argmax(q[new_state])

                q[state, action] += alpha * (
                    reward + gamma * q[new_state, next_action] - q[state, action]
                )

                action = next_action  # SARSA: 下一步用 next_action
            else:
                action = np.argmax(q[new_state])

            state = new_state

        # episode 結束後更新 epsilon
        epsilon = max(epsilon - epsilon_decay_rate, 0)
        if epsilon == 0:
            alpha = 0.0001

        rewards_per_episode[ep] = reward

    env.close()

    # 繪圖
    sum_rewards = np.zeros(episodes)
    for t in range(episodes):
        sum_rewards[t] = np.sum(rewards_per_episode[max(0, t-100):(t+1)])
    plt.plot(sum_rewards)
    plt.savefig('frozen_lake8x8_sarsa.png')

    # 印成功率
    if not is_training:
        print(print_success_rate(rewards_per_episode))

    # 存檔
    if is_training:
        with open("frozen_lake8x8_sarsa.pkl", "wb") as f:
            pickle.dump(q, f)


if __name__ == '__main__':
    run_value_iteration(episodes=15000, render=False, load=False)
    run_value_iteration(episodes=2000, render=False, load=True)

    # run(15000)
    # run(1, is_training=False, render=True)

    # run_sarsa(15000)
    # run_sarsa(2000, is_training=False, render=False)
