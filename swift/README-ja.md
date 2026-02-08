---

## `swift/README-ja.md`（日本語版）

```markdown
# Resilient AI Agent – Swift版

このフォルダには、Resilient AI Agent の **Swift実装版**が含まれています。

本実装は、Python版の設計をもとにした  
**手動変換・再設計バージョン**です。

完成度や速度よりも、  
「読みやすさ」「壊れにくさ」「理解しやすさ」を重視しています。

---

## 目的

Swift版の目的は以下の通りです。

- Resilient AI Agent の設計思想を Swift で表現する
- 学習・検証用の読みやすいサンプルを提供する
- iOS / macOS / CLI への拡張の土台にする

**商用や実運用を前提としたAIではありません。**

---

## 設計方針

- 状態は明示的に扱う
- 複雑な抽象化よりもシンプルな構造
- 「将来の自分」が読み返せるコードを書く

---

## フォルダ構成

```text
swift/
├─ README.md        # 英語版README
├─ README-ja.md     # 日本語版README（このファイル）
└─ ResilientAI.swift