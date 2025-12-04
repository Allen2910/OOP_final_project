# 🤖 Part 3 最終專題：物件導向強化學習 (OOP Reinforcement Learning)

## 🎯 專題目標：示範物件導向設計

本專案的核心目標並非追求最高的 RL 訓練分數，而是透過設計一個 RL 代理器 (Agent) 框架，完整且清晰地示範 **物件導向程式設計 (OOP)** 的三大核心概念：**封裝 (Encapsulation)**、**繼承 (Inheritance)** 與 **多型 (Polymorphism)**。

專案以一個自定義的 **倉庫機器人尋路環境 (Warehouse Robot Environment)** 作為應用背景。

---

## 📂 專案結構

我們採用標準的 Agent/Environment 分層結構，並將 Agent 結構抽象化，以實現高內聚、低耦合的設計。
part3/

├── oop_project_env.py    # Gymnasium 環境介面 (Env Wrapper)
├── warehouse_robot.py    # 環境核心邏輯 (Pygame 渲染與遊戲規則)
├── models/               # 訓練後模型的儲存目錄 (由 runner 創建)
└── src/
    ├── base_agent.py     # 【基底抽象類別】BaseWarehouseAgent
    ├── agents.py         # 【派生具體類別】QLearningAgent, SARSAAgent
    └── main_runner.py    # 【執行器】示範多型訓練迴圈

## 🌟 OOP 概念展示與實現

本專案主要透過 Agent 的設計來實現 OOP 概念：

### 1. 繼承 (Inheritance)

* **基底類別：** `BaseWarehouseAgent` (定義在 `src/base_agent.py`)
    * 使用 `abc.ABC` 定義抽象基底類，確保子類別必須實作核心介面。
* **派生類別：** `QLearningAgent` 與 `SARSAAgent` (定義在 `src/agents.py`)
    * 這兩個類別均繼承自 `BaseWarehouseAgent`，繼承了其通用屬性 (`_lr`, `_gamma`, `_epsilon`) 和方法 (`decay_epsilon`, `save_model`)。

### 2. 多型 (Polymorphism)

多型是本專案的核心展示點，透過兩種方式實現：

#### A. 覆寫 (Overriding) - 核心多型

| 類別 | 覆寫方法 | 實作差異 |
| :--- | :--- | :--- |
| `BaseWarehouseAgent` | 抽象方法 `learn()` | 定義介面，無實作 |
| `QLearningAgent` | 具體實作 `learn()` | 採用 **Off-Policy** 的 Q-Learning 更新公式 ( $\mathbf{\max Q(S', a')}$ ) |
| `SARSAAgent` | 具體實作 `learn()` | 採用 **On-Policy** 的 SARSA 更新公式 ( $\mathbf{Q(S', A')}$ ) |

* **展示：** 在 `src/main_runner.py` 中，`run_experiment` 函式接受任何繼承自 `BaseWarehouseAgent` 的實例。訓練迴圈只需呼叫 `agent.learn(...)`，程式會自動根據實例類型 (QL 或 SARSA) 執行各自的更新邏輯。

#### B. 多載 (Overloading) - 透過預設參數

* **方法：** `BaseWarehouseAgent` 中的 `save_model(file_path, include_q_table=True)`
* **實作：** 根據第二個參數 `include_q_table` 的布林值，執行兩種不同的儲存行為 (儲存 Q-Table 或只儲存配置)。

### 3. 封裝 (Encapsulation)

* **Agent 內部狀態：** 在 `BaseWarehouseAgent` 及其子類別中，所有關鍵的內部數據（例如：`self._q_table`, `self._epsilon`, `self._lr`）都使用 **保護屬性 (Protection Attribute)**（以單底線 `_` 開頭）命名。
* **存取控制：** 外部程式碼必須通過公共方法 (`choose_action`, `learn`, `decay_epsilon`) 才能間接修改或訪問這些內部狀態。

---

## 🧠 優化算法與底層原理 (Demo 必考點)

為了示範算法的差異化和技術貢獻，我們使用了兩種不同的時序差分 (TD) 控制算法，它們在 `learn()` 函式中的更新邏輯不同，是多型的最佳體現。

| 特性 | Q-Learning (Off-Policy) | SARSA (On-Policy) |
| :--- | :--- | :--- |
| **目標 (Target)** | $R + \gamma \cdot \max_{a'} Q(S', a')$ | $R + \gamma \cdot Q(S', A')$ |
| **學習內容** | 學習**最優 Q 值** ($Q^*$) | 學習**當前策略的 Q 值** ($Q^\pi$) |
| **安全性** | 傾向於學習**激進**或最優的路徑。 | 考慮策略 $A'$ 的實際選擇，學習路徑更**保守**（例如在懸崖邊緣，SARSA 會更謹慎）。 |
| **應用場景** | 適用於事後分析或離線學習。 | 適用於需要考慮行動安全性或策略穩定性的在線學習。 |