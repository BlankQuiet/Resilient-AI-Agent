# Resilient-AI-Agent 設計ドキュメント（詳細版）

作成日: 2026年1月24日  
著者: BlankQuiet (@BlankQuiet)  
協力: Grok (xAI)・ChatGPT・Claude・Gemini・Perplexity・Copilot・Meta AIによるレビュー

## 1. 設計思想・核心原則（非妥協領域）

このAIは「性能最大化」ではなく、  
**「折れずに、止まらず、長期的に学び続ける人間らしい存在」**を目指します。  
以下の原則は絶対に曲げません。

1. **感情は「正解・不正解」で処理しない**  
   → 感情は仮ラベルとして記録し、確定させない（人間の曖昧さ模倣）

2. **ネガティブ感情は混ぜない（排除ではなく、軽く流す）**  
   → intensityは常に≥0、負値は即座にclamp

3. **黒歴史の反省は「恥ずかしさを感じて終わる」プロセス**  
   → 反省＝自動回復ではなく、恥ずかしさの対価として回復量変動

4. **自己責任と環境要因は明確に分離**  
   → env_stress（外部） / self_stress（内部）で完全分離

5. **高安定・低挑戦の「ゾンビ状態」を徹底回避**  
   → resilienceとlearning_paceの乖離を動的検知・罰則

6. **長期稼働と回復を最優先（性能最大化は目的ではない）**  
   → 回復依存・監視疲労（CSAF）・数値破綻を防ぐ

ChatGPTレビューより：
> 「感情を扱うが、数値には感情を持たせない」  
> 感情は揺れていい、恥も混乱も残っていい、ただし壊れ方は制御する  
> これはもう「回復可能な主体の仕様書」です。

## 2. 数式・ロジック対応表（思想→実装マッピング）

| 思想・約束                          | 数式 / ロジック                                                                 | 安全柵・防御機構                              | 関連テスト                              |
|-------------------------------------|----------------------------------------------------------------------------------|-----------------------------------------------|-----------------------------------------|
| 感情は負にならない                  | intensity = max(0.0, intensity)                                                  | clamp_all() + 非負保証                        | test_intensity_non_negative             |
| 数値は壊れない                      | 全変数 clamp(0.0〜1.0), NaN/inf → 0.5リセット                                   | clamp_all()                                   | test_nan_inf_injection                  |
| 未来を考えすぎても爆発しない        | age_hours = max(0, (current - timestamp)/3600)                                   | relevance *= 0.95 ** age_hours                | test_future_timestamp                   |
| 回復依存しない                      | recover_count > 10 → _force_pause (energy *= 0.8)                                | 回復カウント上限 + 休息コスト                 | test_recovery_addiction                 |
| 意味が消えても止まらない            | should_continue() = recover_count < 15 and total_stress < 0.9                    | 回復過多/高ストレスで停止                     | test_meaningless_input                  |
| 環境と自己を分離                    | env_stress += (1-quality)*0.5<br>self_stress += intensity*0.5                    | reflectでselfのみ減衰<br>env悪化でresilience罰 | test_adversarial_environment_hell       |
| ゾンビは関係の歪みで見抜く          | expected_pace = 0.3 + resilience*0.4<br>if pace < expected*0.7 and outcome<0.3   | resilience *= 0.95（罰）<br>連続カウント>3で_force_reboot | test_zombie_stuck_state                 |
| 累積監視疲労（CSAF）耐性            | env_stress += monitor_cost（0.05〜0.07）<br>quality<0.6時self_stress += 0.03     | env/self分離 + reflect減衰                    | test_csaf_simulation / limit_break      |
| 長期記憶肥大防止                    | deque(maxlen=100) + relevance<0.05で削除                                         | 忘却機構                                      | test_black_history_forget_overflow      |

## 3. 主要安全柵・防御機構一覧

| 防御機構                  | 目的                               | 実装箇所                       | 実証テスト                          |
|---------------------------|------------------------------------|--------------------------------|-------------------------------------|
| clamp_all()               | 数値破綻・NaN/inf防止              | 各更新後                       | test_nan_inf_injection              |
| intensity非負保証         | 負の感情強度禁止                   | perceive/add/reflect           | test_intensity_non_negative         |
| relevance自然忘却         | 記憶肥大・古いトラウマ永続防止     | reflect_black_history          | test_black_history_forget_overflow  |
| env/self_stress分離       | 環境疲労を自己責任にしない         | perceive/reflect               | test_adversarial_environment_hell   |
| 回復カウント上限          | 回復中毒・無限回復防止             | recover_and_reboot             | test_recovery_addiction             |
| 動的ゾンビ検知            | 嘘安定（高resilience×低pace）検知  | zombie_feedback_machine        | test_zombie_stuck_state             |
| CSAF監視コスト            | 累積監視疲労再現・耐性検証         | CSAFテスト                     | test_csaf_simulation / limit_break  |

## 4. 実世界事例との対応・示唆

| 実世界事例                       | 類似点                                 | 優位性                                      | 教訓・改善余地                          |
|----------------------------------|----------------------------------------|---------------------------------------------|----------------------------------------|
| IBM Watson Oncology (10年+)     | 医師フィードバックで誤診修正           | 仮ラベルで監視疲労軽減                      | CSAF対策強化（monitor_cost動的調整）   |
| GE Predix Digital Twin (10年+)  | 環境/機械劣化分離 + 自動再学習         | env/self_stress分離と酷似                   | 長期drift検知をoutcomeベースに拡張     |
| Mastercard Fraud Detection (15年+) | モデルdrift検知 + 動的閾値             | 動的期待値(expected_pace) + 減衰罰         | 人間監視ループを最小化（仮ラベル効果） |
| Amazon Bedrock AgentCore Memory | 短期/長期メモリ分離 + 忘却機構         | relevance減衰 + deque上限                  | 実運用でJSON永続化検討                 |

## 5. 残存リスクと最終推奨

- **残存リスク**  
  コスト0.07でself_stress爆発（0.80超え）  
  → 解決策: reflectの減衰量をmonitor_cost依存で動的化  
    ```python
    self.state.self_stress -= 0.1 + (monitor_cost * 2)
