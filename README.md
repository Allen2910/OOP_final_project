# AI Project: Reinforcement Learning & Multi-Agent Search

## Project Overview

### Part 1: Test
Basic testing module.

### Part 2: Reinforcement Learning
* **Goal:** Optimize the agent to achieve a total accuracy of at least **70%**.
* **Environment:** Frozen Lake (Gymnasium).

### Part 3: Cooperative Search (A* Algorithm)
The goal of this project is to locate the "Kaggle" target on a map. Two robots (Bot A and Bot B) utilize the A* algorithm to find the target together.

* **Heuristic:** Manhattan Distance.
* **Collision:** Each bot regards the other as an obstacle/block.
* **Strategy:**
    * **Bot A:** Target is "Kaggle".
    * **Bot B:** Initially targets Bot A. If Bot B's distance to "Kaggle" is less than **5 steps**, Bot B's target switches to "Kaggle".

---

## Dependencies

Please ensure you have the following libraries installed:

### Part 2 Libraries
* `pickle`
* `numpy`
* `matplotlib`
* `gymnasium`

### Part 3 Libraries
* `pygame`

*(Note: The project also uses a local `sprites` module to render the pictures of bots, floors, and kaggles.)*

---

## How to Run

### Part 2 Execution
Run the Reinforcement Learning script:
```bash
python ./frozen_lake.py
```

### Part 3 Execution
Run the main A* search simulation:
```bash
python main.py
```

## Contribution List

| Student ID | Name | Contribution | Content |
| :--- | :--- | :--- | :--- |
| **B123040030** | 劉兆涵 | **40%** | Finished Part 2 |
| **B123040031** | 許耕瑜 | **30%** | Finished Part 3 |
| **B123040010** | 王紹庭 | **30%** | Finished PPT |