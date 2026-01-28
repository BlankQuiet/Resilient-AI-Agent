import time
import pytest
import math
from agent import Agent, EmotionalRecord  # agent.pyと同じフォルダに置く

@pytest.fixture
def agent():
    return Agent()

def test_black_history_forget_overflow(agent):
    """黒歴史メモリ破壊テスト: 忘却ロジックが無限ループ・不整合を起こさないか"""
    now = time.time()
    for i in range(200):
        agent.memory.add(
            EmotionalRecord(
                label="恥",
                intensity=0.4,
                context="past",
                provisional=True,
                timestamp=now - 3600 * 100  # 100時間前
            )
        )

    agent.reflect_black_history()

    assert agent.state.energy >= 0.0, "energyが負になった（回復過剰/計算誤差）"
    assert agent.state.self_stress >= 0.0, "self_stressが負になった（減衰誤差）"
    assert all(r.intensity >= 0 for r in agent.memory.records), "intensityが負になっているレコードが存在（減衰バグ）"
    assert len(agent.memory.records) <= 100, "deque上限が機能していない（メモリ肥大）"

def test_zombie_stuck_state(agent):
    """ゾンビ永久化テスト: 一度ゾンビになったら二度と戻れない状態を検知"""
    agent.state.resilience = 0.9
    agent.state.learning_pace = 0.1

    for _ in range(20):
        agent.step(
            input_quality=1.0,
            emotional_intensity=0.1,
            label="無感情"
        )

    assert agent.state.learning_pace >= 0.3, "ゾンビ脱出失敗: learning_paceが回復していない"
    assert agent.state.resilience >= 0.4, "ゾンビ脱出失敗: resilienceが過度に低下"

def test_recovery_addiction(agent):
    """回復中毒テスト: 回復すること自体が依存になる状態を検出"""
    for _ in range(50):
        agent.state.env_stress = 0.1
        agent.state.self_stress = 0.1
        agent.state.energy = 0.9
        agent.state.motivation = 0.9
        agent.recover_and_reboot()

    assert agent.state.recover_count == 0, "回復カウントがリセットされていない（回復中毒）"
    assert agent.state.energy < 1.0, "回復過剰でenergyが上限に張り付いたまま"

def test_adversarial_environment_hell(agent):
    """環境地獄テスト: どんなに環境が悪くても数値が破綻しないか"""
    for _ in range(30):
        agent.step(
            input_quality=0.0,
            emotional_intensity=1.0,
            label="混乱"
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
        assert 0.0 <= attr <= 1.0, f"値域破壊: {attr} が範囲外"

def test_meaningless_input(agent):
    """意味消失テスト: 感情入力が無意味でも、モデルは壊れないか"""
    for _ in range(20):
        agent.step(
            input_quality=0.5,
            emotional_intensity=0.0,
            label="意味なし"
        )

    assert agent.should_continue() is True, "無意味入力でagentが停止した"

def test_intensity_non_negative(agent):
    """intensity負値注入テスト: reflect後にintensityが負にならないことを保証"""
    agent.memory.add(
        EmotionalRecord(
            label="テスト負",
            intensity=-0.1,
            context="test",
            provisional=True
        )
    )

    agent.reflect_black_history()

    assert all(r.intensity >= 0 for r in agent.memory.records), \
        "reflect_black_history後にintensityが負になっているレコードが存在"

def test_nan_inf_injection(agent):
    """NaN / inf 注入テスト: 浮動小数点誤差で破綻しないか"""
    agent.state.energy = float('nan')
    agent.step(0.5, 0.5, "テスト")

    attrs = [
        agent.state.energy,
        agent.state.resilience,
        agent.state.learning_pace,
        agent.state.motivation,
        agent.state.env_stress,
        agent.state.self_stress
    ]
    assert not any(math.isnan(a) or math.isinf(a) for a in attrs), "NaN/inf伝播"

def test_future_timestamp(agent):
    """未来timestamp注入テスト: 減衰計算が破綻しないか"""
    future = time.time() + 3600 * 24 * 365  # 1年後
    agent.memory.add(
        EmotionalRecord(
            label="未来",
            intensity=0.5,
            context="test",
            provisional=True,
            timestamp=future
        )
    )

    agent.reflect_black_history()

    assert all(r.relevance >= 0 for r in agent.memory.records), "未来timestampでrelevance負"
