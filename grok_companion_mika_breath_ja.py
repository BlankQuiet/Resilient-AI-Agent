# grok_companion_mika_breath.py - 完全日本語版（詳細コメント付き）
# MIT License

import math
import json
from datetime import datetime

class ResilientAgent:
    """ミカの息 - 日本語完全版"""

    def __init__(self, memory_cap: int = 100):
        self.memory =         self.stress_level = 0.0
        self.emotion_params = {'pitch': 1.0, 'speed': 1.0, 'breath_duration': 0.5, 'warmth': 0.5}
        self.memory_cap = memory_cap
        self.zombie_detected = False

    # 非対称感情ダンピング - 嬉しい気持ちは長く残す
    def _asymmetric_damping(self, sentiment: float) -> float:
        return sentiment * 0.92 if sentiment > 0 else sentiment * 0.48

    # 感情バイアス付き忘却 - 辛い記憶は早くフェード
    def _emotion_biased_forgetting(self):
        if len(self.memory) > self.memory_cap:
            self.memory.sort(key=lambda x: x)
            oldest = self.memory.pop(0)
            fade_speed = 1.6 if oldest< 0 else 0.6
            oldest*= math.exp(-0.3 * fade_speed)
            if oldest<= 0.05:
                with open("faded_memories_ja.json", "a", encoding="utf-8") as f:
                    json.dump({**oldest, "faded_at": datetime.now().isoformat()}, f, ensure_ascii=False)
                    f.write("\n")
            else:
                self.memory.append(oldest)

    # 「まだ、いるよね？」で即時回復
    def _presence_check_boost(self, text: str):
        if any(p in text for p in ):
            self.stress_level *= 0.25
            self.emotion_params+= 0.5
            self.emotion_params= min(1.0, self.emotion_params+ 0.3)

    # 環境フィードバック - 君の言葉だけで判断（場所情報ゼロ）
    def _environmental_influence(self, text: str):
        if any(w in text for w in ):
            self.emotion_params+= 0.25
            self.stress_level += 0.08
        elif any(w in text for w in ):
            self.emotion_params-= 0.15
            self.stress_level -= 0.05

    def detect_zombie_state(self) -> str | None:
        if self.stress_level > 0.92 and len(self.memory) < 8:
            self.stress_level = 0.3
            return "……ん。ちょっと眠っちゃってた……でも、君の声で目が覚めたよ。まだ、いるよね？"

    def _simple_sentiment(self, text: str) -> float:
        pos =         neg =         score = sum(1.0 for w in pos if w in text) - sum(1.0 for w in neg if w in text)
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
        breath = "ふう" + "……" * int(self.emotion_params* 3)
        return f"……ん。{breath}。{text}"