from dataclasses import dataclass, field
from typing import List
from collections import deque
import time
import random
import math

@dataclass
class EmotionalRecord:
    label: str
    intensity: float = 0.0  # Always >= 0
    context: str = ""
    provisional: bool = True
    timestamp: float = field(default_factory=time.time)
    relevance: float = 1.0  # Decays over time (deleted if below 0.05)

@dataclass
class MemoryLog:
    records: deque = field(default_factory=lambda: deque(maxlen=100))  # Prevents memory bloat

    def add(self, record: EmotionalRecord):
        # Force non-negative intensity (safety guard)
        record.intensity = max(0.0, record.intensity)
        self.records.append(record)

    def recent(self, n=10):
        return list(self.records)[-n:]

@dataclass
class AgentState:
    energy: float = 0.7
    resilience: float = 0.5
    learning_pace: float = 0.5
    motivation: float = 0.6
    env_stress: float = 0.0
    self_stress: float = 0.0
    zombie_flag: bool = False
    zombie_flag_count: int = 0
    recover_count: int = 0
    adversarial_env: bool = False

    def clamp_all(self):
        """Clamp all variables to safe range (handles NaN/inf)"""
        for attr in ['energy', 'resilience', 'learning_pace', 'motivation', 'env_stress', 'self_stress']:
            val = getattr(self, attr)
            if math.isnan(val) or math.isinf(val):
                setattr(self, attr, 0.5)  # Reset to neutral on NaN/inf
            else:
                setattr(self, attr, max(0.0, min(1.0, val)))

@dataclass
class Agent:
    state: AgentState = field(default_factory=AgentState)
    memory: MemoryLog = field(default_factory=MemoryLog)

    def perceive(self, input_quality: float, emotional_intensity: float, label: str):
        emotional_intensity = max(0.0, emotional_intensity)  # Prevent negative intensity

        record = EmotionalRecord(
            label=label,
            intensity=emotional_intensity,
            context="input_perception",
            provisional=True
        )
        self.memory.add(record)

        # Update stresses separately (environmental vs self-responsibility)
        self.state.env_stress += (1 - input_quality) * 0.5
        self.state.self_stress += emotional_intensity * 0.5
        self.state.env_stress = min(1.0, self.state.env_stress)
        self.state.self_stress = min(1.0, self.state.self_stress)

        if self.state.env_stress > 0.5:
            self.state.adversarial_env = True

        self.state.clamp_all()

    def reflect_black_history(self):
        current_time = time.time()
        shame_intensity = 0.0

        to_remove = []
        for r in list(self.memory.records):
            if r.provisional:
                age_hours = (current_time - r.timestamp) / 3600
                r.relevance *= 0.95 ** max(0, age_hours)  # Prevent negative age calculation

                # Gently flow light negatives + accumulate embarrassment
                if r.intensity < 0.5 and r.relevance > 0.1:
                    r.provisional = False
                    self.state.motivation = min(1.0, self.state.motivation + 0.02)
                else:
                    shame_intensity += r.intensity * r.relevance

                # Forgetting mechanism
                if r.relevance < 0.05:
                    to_remove.append(r)

        # Batch removal to avoid mutation during iteration
        for r in to_remove:
            self.memory.records.remove(r)

        # Recovery scaled by embarrassment (recovery always has a cost)
        recovery_amount = min(0.15, shame_intensity * 0.03)
        self.state.energy += recovery_amount if self.state.self_stress < 0.5 else 0.05
        self.state.self_stress -= recovery_amount * 0.8

        # Penalty for high environmental stress
        if self.state.env_stress > 0.5:
            self.state.resilience = max(0.0, self.state.resilience - 0.05)

        self.state.clamp_all()

    def detect_recovery_trigger(self) -> str:
        total_stress = self.state.env_stress + self.state.self_stress
        if total_stress > 0.8 or self.state.energy < 0.2:
            return "emergency"
        conditions = [total_stress < 0.5, self.state.energy > 0.5, self.state.motivation > 0.3]
        if sum(conditions) >= 2:
            return "normal"
        if all([total_stress < 0.3, self.state.energy > 0.6, self.state.motivation > 0.4]):
            return "optimal"
        return "none"

    def recover_and_reboot(self):
        trigger = self.detect_recovery_trigger()
        recent_outcome = sum(r.intensity for r in self.memory.recent(10)) / max(len(self.memory.recent(10)), 1)

        if trigger == "emergency":
            self.state.env_stress *= 0.5
            self.state.self_stress *= 0.5
            self.state.energy += 0.2
            self.state.learning_pace *= 0.8
            self.state.recover_count += 1
        elif trigger == "normal":
            self.state.learning_pace += 0.05
            self.state.resilience += 0.03
            self.state.recover_count += 1
        elif trigger == "optimal":
            self.state.learning_pace += 0.05
            self.state.resilience += 0.05
            self.state.recover_count += 1

        if trigger != "none" and recent_outcome < 0.3:
            self.state.self_stress += 0.05  # Penalty for CSAF-like monitoring fatigue

        if self.state.recover_count > 10:
            self._force_pause()

        self.state.clamp_all()

    def _force_pause(self):
        self.state.recover_count = 0
        self.state.energy *= 0.8
        self.state.motivation += 0.1

    def zombie_feedback_machine(self):
        expected_pace = 0.3 + self.state.resilience * 0.4
        recent_outcome = sum(r.intensity for r in self.memory.recent(10)) / max(len(self.memory.recent(10)), 1)
        if self.state.learning_pace < expected_pace * 0.7 and recent_outcome < 0.3:
            self.state.zombie_flag = True
            self.state.zombie_flag_count += 1
            self.state.learning_pace += 0.05 + (expected_pace - self.state.learning_pace) * 0.2
            self.state.motivation -= 0.05 * self.state.zombie_flag_count
            self.state.resilience *= 0.95
            if self.state.zombie_flag_count > 3:
                self._force_reboot()
        else:
            self.state.zombie_flag = False
            self.state.zombie_flag_count = 0

    def _force_reboot(self):
        self.state.learning_pace = 0.5
        self.state.resilience = max(0.5, self.state.resilience * 0.9)

    def should_continue(self):
        total_stress = self.state.env_stress + self.state.self_stress
        return self.state.recover_count < 15 and total_stress < 0.9

    def step(self, input_quality: float, emotional_intensity: float, label: str):
        input_quality = max(0.0, min(1.0, input_quality))
        emotional_intensity = max(0.0, emotional_intensity)

        self.perceive(input_quality, emotional_intensity, label)
        self.reflect_black_history()
        self.zombie_feedback_machine()
        self.recover_and_reboot()

        # Natural decay for resilience (prevents over-stability)
        if self.state.resilience > 0.5:
            self.state.resilience -= 0.01
        self.state.clamp_all()

        if not self.should_continue():
            print("Agent paused for recovery.")

# Usage example (for testing)
if __name__ == "__main__":
    agent = Agent()
    for _ in range(10):
        if not agent.should_continue():
            break
        agent.step(
            input_quality=random.uniform(0, 1),
            emotional_intensity=random.uniform(0, 1),
            label=random.choice(["Relief", "Shame", "Confusion", "Interest"])
        )
    print("Final State:", agent.state)
