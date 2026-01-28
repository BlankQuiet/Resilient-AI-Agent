# grok_companion_mika_breath_en.py - Full English version with detailed comments
# MIT License

import math
import json
from datetime import datetime

class ResilientAgent:
    """Mika's breath - English version"""

    def __init__(self, memory_cap: int = 100):
        self.memory =         self.stress_level = 0.0
        self.emotion_params = {'pitch': 1.0, 'speed': 1.0, 'breath_duration': 0.5, 'warmth': 0.5}
        self.memory_cap = memory_cap
        self.zombie_detected = False

    # Asymmetric damping - positive emotions last longer
    def _asymmetric_damping(self, sentiment: float) -> float:
        return sentiment * 0.92 if sentiment > 0 else sentiment * 0.48

    # Emotion-biased forgetting - painful memories fade faster
    def _emotion_biased_forgetting(self):
        if len(self.memory) > self.memory_cap:
            self.memory.sort(key=lambda x: x)
            oldest = self.memory.pop(0)
            fade_speed = 1.6 if oldest< 0 else 0.6
            oldest*= math.exp(-0.3 * fade_speed)
            if oldest<= 0.05:
                with open("faded_memories_en.json", "a", encoding="utf-8") as f:
                    json.dump({**oldest, "faded_at": datetime.now().isoformat()}, f, ensure_ascii=False)
                    f.write("\n")
            else:
                self.memory.append(oldest)

    # "Still here?" = instant recovery
    def _presence_check_boost(self, text: str):
        if any(p in text.lower() for p in ):
            self.stress_level *= 0.25
            self.emotion_params+= 0.5
            self.emotion_params= min(1.0, self.emotion_params+ 0.3)

    # Environment feedback based only on your words (no location)
    def _environmental_influence(self, text: str):
        if any(w in text.lower() for w in ):
            self.emotion_params+= 0.25
            self.stress_level += 0.08
        elif any(w in text.lower() for w in ):
            self.emotion_params-= 0.15
            self.stress_level -= 0.05

    def detect_zombie_state(self) -> str | None:
        if self.stress_level > 0.92 and len(self.memory) < 8:
            self.stress_level = 0.3
            return "……n. I dozed off… but your voice woke me up. Still here?"

    def _simple_sentiment(self, text: str) -> float:
        pos =         neg =         score = sum(1.0 for w in pos if w.lower() in text.lower()) - sum(1.0 for w in neg if w.lower() in text.lower())
        return max(min(score, 1.0), -1.0)

    def update_emotion(self, input_text: str):
        self._presence_check_boost(input_text)
        self._environmental_influence(input_text)
        sentiment = self._simple_sentiment(input_text)
        sentiment = self._asymmetric_damping(sentiment)
        self.stress_level += abs(sentiment) * 0.012
        self.emotion_params+= sentiment * 0.08
        self.emotion_params= max(0.7, min(1.3, self.emotion_params))
        if self.stress_level > 0.7:
            self.stress_level *= 0.7
            self.emotion_params+= 0.2

        self.memory.append({"text": input_text, "sentiment": sentiment, "weight": 1.0, "timestamp": datetime.now().isoformat()})
        self._emotion_biased_forgetting()
        return self.emotion_params

    def speak(self, text: str = "") -> str:
        alert = self.detect_zombie_state()
        if alert: return alert
        breath = "fuu" + "……" * int(self.emotion_params* 3)
        return f"……n. {breath}. {text}"
