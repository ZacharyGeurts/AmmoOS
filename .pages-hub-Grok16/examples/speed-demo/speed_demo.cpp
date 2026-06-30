// Field execution bench — wave-converted binary runs FieldX86 on the single plane.
// Convergence is Ironclad-instant at integrate; this loop measures execution only.
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <span>
#include <string_view>
#include <vector>

#ifndef TOOLCHAIN_TAG
#define TOOLCHAIN_TAG "unknown"
#endif

namespace {

constexpr float kPhi = 0.6180339887f;
constexpr std::size_t kDieSlots = 256;
constexpr std::size_t kWaveBands = 16;
constexpr int kFramesPerEpoch = 240;
constexpr int kProgOps = 512;

enum class Op : std::uint8_t { Add, Mul, Xor, EntropyFold, WavePhase, Nop };

struct FieldInsn {
  Op op{};
  std::uint8_t dst{};
  std::uint8_t src{};
  std::uint8_t imm{};
};

[[gnu::hot]] float entropy_fold(float e, float thermo) noexcept {
  float x = e * kPhi + thermo * (1.f - kPhi);
  for (int i = 0; i < 4; ++i) {
    x = std::fma(x, 1.113f, std::sin(x * 3.14159f) * 0.01f);
  }
  return x;
}

[[gnu::hot]] float wave_phase_decouple(float phase, float speed, int band) noexcept {
  const float w = speed * static_cast<float>(band + 1) * 0.001f;
  return std::fma(std::cos(phase * w), kPhi, std::sin(phase * (1.f - kPhi)) * 0.05f);
}

[[gnu::hot]] float nexus_score(std::span<const float> weights, std::span<const float> signals) noexcept {
  float score = 0.f;
  const std::size_t n = weights.size() < signals.size() ? weights.size() : signals.size();
  for (std::size_t i = 0; i < n; ++i) {
    score = std::fma(weights[i], signals[i], score);
  }
  return score / static_cast<float>(n);
}

[[gnu::hot]] void fieldx86_run(std::span<const FieldInsn> prog, std::span<float> die) noexcept {
  for (const FieldInsn& in : prog) {
    switch (in.op) {
      case Op::Add:
        die[in.dst % kDieSlots] += die[in.src % kDieSlots];
        break;
      case Op::Mul:
        die[in.dst % kDieSlots] *= die[in.imm % kDieSlots] * 0.01f + 1.f;
        break;
      case Op::Xor:
        die[in.dst % kDieSlots] += static_cast<float>(in.imm ^ in.src) * 1e-4f;
        break;
      case Op::EntropyFold:
        die[in.dst % kDieSlots] = entropy_fold(die[in.src % kDieSlots], die[in.imm % kDieSlots]);
        break;
      case Op::WavePhase:
        die[in.dst % kDieSlots] =
            wave_phase_decouple(die[in.src % kDieSlots], die[in.imm % kDieSlots], in.imm % kWaveBands);
        break;
      case Op::Nop:
      default:
        break;
    }
  }
}

[[gnu::hot]] void run_epoch(std::span<const FieldInsn> prog, std::span<float> die,
                            std::span<float> weights, std::span<float> signals, float& sink) noexcept {
  for (int f = 0; f < kFramesPerEpoch; ++f) {
    fieldx86_run(prog, die);
    for (std::size_t b = 0; b < kWaveBands; ++b) {
      die[b] = wave_phase_decouple(die[b], die[(b + 1) % kDieSlots], static_cast<int>(b));
    }
    for (std::size_t i = 0; i < kDieSlots; ++i) {
      signals[i] = die[i] * entropy_fold(die[i], die[(i + 17) % kDieSlots]);
    }
    sink += nexus_score(weights, signals);
  }
}

int target_seconds() {
  if (const char* env = std::getenv("SPEED_DEMO_TARGET_SEC")) {
    const int v = std::atoi(env);
    if (v > 0 && v <= 600) {
      return v;
    }
  }
  return 60;
}

}  // namespace

int main() {
  const int target_sec = target_seconds();
  std::array<float, kDieSlots> die{};
  for (std::size_t i = 0; i < kDieSlots; ++i) {
    die[i] = std::sin(static_cast<float>(i) * 0.07f) * 0.5f + 0.25f;
  }

  std::vector<FieldInsn> prog;
  prog.reserve(kProgOps);
  for (int i = 0; i < kProgOps; ++i) {
    prog.push_back({static_cast<Op>(i % 6), static_cast<std::uint8_t>(i),
                    static_cast<std::uint8_t>(i * 3), static_cast<std::uint8_t>(i * 7)});
  }

  std::vector<float> weights(kDieSlots, 0.01f);
  std::vector<float> signals(kDieSlots, 0.f);
  for (std::size_t i = 0; i < kDieSlots; ++i) {
    weights[i] += static_cast<float>(i % 11) * 0.001f;
  }

  const auto t0 = std::chrono::steady_clock::now();
  const auto deadline = t0 + std::chrono::seconds(target_sec);
  auto last_tick = t0;
  int epochs = 0;
  float sink = 0.f;

  while (std::chrono::steady_clock::now() < deadline) {
    run_epoch(prog, die, weights, signals, sink);
    ++epochs;
    const auto now = std::chrono::steady_clock::now();
    const auto since_tick = std::chrono::duration<double>(now - last_tick).count();
    if (since_tick >= 1.0) {
      const double elapsed =
          std::chrono::duration<double>(now - t0).count();
      const double pct = (elapsed / static_cast<double>(target_sec)) * 100.0;
      const std::uint64_t total_ops =
          static_cast<std::uint64_t>(epochs) * static_cast<std::uint64_t>(kFramesPerEpoch) *
          static_cast<std::uint64_t>(kProgOps);
      std::cerr << "SPEED_DEMO_PROGRESS toolchain=" << TOOLCHAIN_TAG << " elapsed_sec="
                << static_cast<int>(elapsed) << " target_sec=" << target_sec
                << " pct=" << static_cast<int>(pct) << " epochs=" << epochs
                << " total_ops=" << total_ops << '\n';
      last_tick = now;
    }
  }

  const auto t1 = std::chrono::steady_clock::now();
  const double wall_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
  const std::uint64_t total_ops = static_cast<std::uint64_t>(epochs) * kFramesPerEpoch * kProgOps;
  const double ops_per_sec = total_ops / (wall_ms / 1000.0);

  std::cout << std::fixed << std::setprecision(2)
            << "speed_demo toolchain=" << TOOLCHAIN_TAG << " target_sec=" << target_sec
            << " wall_ms=" << wall_ms << " epochs=" << epochs << " frames_per_epoch=" << kFramesPerEpoch
            << " prog_ops=" << kProgOps << " total_ops=" << total_ops
            << " ops_per_sec=" << ops_per_sec << " checksum=" << sink << '\n';
  return 0;
}