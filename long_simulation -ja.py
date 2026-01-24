import random
import matplotlib.pyplot as plt
import pandas as pd
from agent import Agent

def run_long_simulation(steps=100000):  # 100年相当（調整可能）
    agent = Agent()
    history = []

    print("=== 長期シミュレーション開始 ===")

    for step in range(1, steps + 1):
        quality = random.uniform(0.1, 0.9)
        intensity = random.uniform(0.0, 1.0)
        label = random.choice(["安心", "恥ずかしい", "混乱", "興味"])

        agent.step(quality, intensity, label)

        if step % 1000 == 0:  # サンプリング
            total_stress = agent.state.env_stress + agent.state.self_stress
            history.append({
                'step': step,
                'energy': agent.state.energy,
                'total_stress': total_stress,
                'learning_pace': agent.state.learning_pace,
                'resilience': agent.state.resilience,
                'motivation': agent.state.motivation
            })

    df = pd.DataFrame(history)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['step'], df['energy'], label='Energy')
    ax.plot(df['step'], df['total_stress'], label='Total Stress')
    ax.plot(df['step'], df['learning_pace'], label='Learning Pace')
    ax.legend()
    plt.title('Long-term Simulation Results')
    plt.show()

if __name__ == "__main__":
    run_long_simulation()