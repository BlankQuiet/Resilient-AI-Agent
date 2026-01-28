// ResilientAI.swift
// Swift translation of the Python reference implementation
// Core behavior is intentionally preserved.

import Foundation

final class ResilientAI {

    // MARK: - Configuration (Design constants)

    /// Hard upper bound for stress (must never be exceeded)
    private let stressHardCap: Double = 0.20

    /// Maximum number of memories kept
    private let memoryLimit: Int = 50
    // ③ Future note:
    // memoryLimit can be injected via initializer for testing or expansion.

    /// Phrases that mark a memory as positive (never forgotten)
    private let positiveCore: [String] = [
        "thank",
        "thanks",
        "appreciate",
        "good",
        "nice",
        "kind"
    ]

    /// Keywords that increase stress
    private let negativeKeywords: [String] = [
        "angry",
        "tired",
        "hate",
        "annoy",
        "bad"
    ]

    // MARK: - Internal State

    private var stressLevel: Double = 0.0
    private var memory: [String] = []

    // ③ Future note:
    // If used asynchronously, protect stressLevel and memory
    // using `actor` or DispatchQueue.

    // MARK: - Public API

    /// Process an input text and update internal state.
    func processText(_ text: String) {
        let lower = text.lowercased()

        // Detect positive input
        if isPositive(lower) {
            // Recovery-first design:
            // Positive input immediately reduces stress.
            stressLevel = max(0.0, stressLevel - 0.05)
        }

        // Detect negative input
        if isNegative(lower) {
            stressLevel += 0.02
        }

        // Enforce hard stress cap (must be applied unconditionally)
        stressLevel = min(stressLevel, stressHardCap)

        storeMemory(text)
    }

    /// Returns current status.
    /// ② Readability note:
    /// Returning a struct would be more Swift-idiomatic than [String: Any].
    func status() -> [String: Any] {
        return [
            "stress": Double(round(stressLevel * 1000) / 1000),
            "memoryCount": memory.count
        ]
    }

    // MARK: - Memory Handling

    private func storeMemory(_ text: String) {
        memory.append(text)

        if memory.count > memoryLimit {
            emotionBiasedForgetting()
        }
    }

    /// Removes the first non-positive-core memory.
    /// Positive-core memories are never deleted.
    private func emotionBiasedForgetting() {
        // ② Readability improvement:
        // Using firstIndex(where:) makes intent clearer
        if let index = memory.firstIndex(where: { old in
            !positiveCore.contains(where: { keyword in
                old.lowercased().contains(keyword)
            })
        }) {
            memory.remove(at: index)
        }
    }

    // MARK: - Keyword Detection

    private func isPositive(_ text: String) -> Bool {
        return positiveCore.contains(where: { text.contains($0) })
    }

    private func isNegative(_ text: String) -> Bool {
        return negativeKeywords.contains(where: { text.contains($0) })
    }
}