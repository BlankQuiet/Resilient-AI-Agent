import random
import matplotlib.pyplot as plt
import pandas as pd
from agent import Agent  # Import the core agent from agent.py

def run_long_simulation(steps=100000):  # Equivalent to 100 years (adjustable)
    agent = Agent()
    history = []

    print("=== Long-term Simulation Started ===")

    for step in range(1, steps + 1):
        # Generate random input to simulate real-world variability
        quality = random.uniform(0.1, 0.9)
        intensity = random.uniform(0.0, 1.0)
        label = random.choice(["Relief", "Shame", "Confusion", "Interest"])

        agent.step(quality, intensity, label)

        # Sample every 1000 steps to save memory and avoid overload
        if step % 1000 == 0:
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

    # Create plots for visualization
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['step'], df['energy'], label='Energy')
    ax.plot(df['step'], df['total_stress'], label='Total Stress')
    ax.plot(df['step'], df['learning_pace'], label='Learning Pace')
    ax.legend()
    plt.title('Long-term Simulation Results')
    plt.xlabel('Steps')
    plt.ylabel('Value')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    run_long_simulation()
