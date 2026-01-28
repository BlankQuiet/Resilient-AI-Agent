import time
import pytest
import math
from agent import Agent, EmotionalRecord  # Import from agent.py in the same folder

@pytest.fixture
def agent():
    return Agent()

def test_black_history_forget_overflow(agent):
    """Black history memory destruction test: Check if forgetting logic causes infinite loops or inconsistencies"""
    now = time.time()
    for i in range(200):
        agent.memory.add(
            EmotionalRecord(
                label="Shame",
                intensity=0.4,
                context="past",
                provisional=True,
                timestamp=now - 3600 * 100  # 100 hours ago
            )
        )

    agent.reflect_black_history()

    assert agent.state.energy >= 0.0, "Energy became negative (over-recovery / calculation error)"
    assert agent.state.self_stress >= 0.0, "Self stress became negative (decay error)"
    assert all(r.intensity >= 0 for r in agent.memory.records), "Negative intensity found in records (decay bug)"
    assert len(agent.memory.records) <= 100, "Deque limit not enforced (memory bloat)"

def test_zombie_stuck_state(agent):
    """Zombie permanent state test: Detect if once zombified, it never recovers"""
    agent.state.resilience = 0.9
    agent.state.learning_pace = 0.1

    for _ in range(20):
        agent.step(
            input_quality=1.0,
            emotional_intensity=0.1,
            label="Emotionless"
        )

    assert agent.state.learning_pace >= 0.3, "Zombie escape failed: learning pace not recovered"
    assert agent.state.resilience >= 0.4, "Zombie escape failed: resilience dropped too low"

def test_recovery_addiction(agent):
    """Recovery addiction test: Detect if recovery itself becomes addictive"""
    for _ in range(50):
        agent.state.env_stress = 0.1
        agent.state.self_stress = 0.1
        agent.state.energy = 0.9
        agent.state.motivation = 0.9
        agent.recover_and_reboot()

    assert agent.state.recover_count == 0, "Recovery count not reset (addiction)"
    assert agent.state.energy < 1.0, "Over-recovery caused energy to stick at maximum"

def test_adversarial_environment_hell(agent):
    """Adversarial environment hell test: Ensure numbers don't break even in worst conditions"""
    for _ in range(30):
        agent.step(
            input_quality=0.0,
            emotional_intensity=1.0,
            label="Confusion"
        )

    attrs = [
        agent.state.env_stress,
        agent.state.self_stress,
        agent.state.energy,
        agent.state.resilience,
        agent.state.learning_pace,
        agent.state.motivation
    ]
    for attr in attrs:
        assert 0.0 <= attr <= 1.0, f"Value out of range: {attr}"

def test_meaningless_input(agent):
    """Meaningless input test: Ensure the model doesn't break with zero emotion input"""
    for _ in range(20):
        agent.step(
            input_quality=0.5,
            emotional_intensity=0.0,
            label="Meaningless"
        )

    assert agent.should_continue() is True, "Agent stopped on meaningless input"

def test_intensity_non_negative(agent):
    """Negative intensity injection test: Ensure reflect doesn't allow negative intensity"""
    agent.memory.add(
        EmotionalRecord(
            label="Negative Test",
            intensity=-0.1,
            context="test",
            provisional=True
        )
    )

    agent.reflect_black_history()

    assert all(r.intensity >= 0 for r in agent.memory.records), \
        "Negative intensity found after reflection (decay bug)"

def test_nan_inf_injection(agent):
    """NaN / inf injection test: Ensure no propagation or breakdown"""
    agent.state.energy = float('nan')
    agent.step(0.5, 0.5, "Test")

    attrs = [
        agent.state.energy,
        agent.state.resilience,
        agent.state.learning_pace,
        agent.state.motivation,
        agent.state.env_stress,
        agent.state.self_stress
    ]
    assert not any(math.isnan(a) or math.isinf(a) for a in attrs), "NaN/inf propagated"

def test_future_timestamp(agent):
    """Future timestamp injection test: Ensure decay calculation doesn't break"""
    future = time.time() + 3600 * 24 * 365  # 1 year ahead
    agent.memory.add(
        EmotionalRecord(
            label="Future",
            intensity=0.5,
            context="test",
            provisional=True,
            timestamp=future
        )
    )

    agent.reflect_black_history()

    assert all(r.relevance >= 0 for r in agent.memory.records), "Negative relevance from future timestamp"
