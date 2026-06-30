// Field-Opt bench: FieldX86 dispatch + entropy fold + wave phase + NEXUS scoring
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <span>
#include <vector>

#if defined(GROK16_BELT_2_0)
constexpr const char* kProfile = "belt_2_0";
#elif defined(GROK16_BELT_1_0)
constexpr const char* kProfile = "belt_1_0";
#elif defined(GROK16_PROFILE_FIELD_OPT)
constexpr const char* kProfile = "field_opt";
#elif defined(GROK16_PROFILE_AI)
constexpr const char* kProfile = "ai";
#elif defined(GROK16_PROFILE_FIELD)
constexpr const char* kProfile = "field_compute";
#else
constexpr const char* kProfile = "default";
#endif

namespace {

constexpr float kPhi = 0.6180339887f;
#if defined(GROK16_BELT_2_0)
constexpr std::size_t kDieSlots = 512;
constexpr std::size_t kBeltChunk = 64;
constexpr std::size_t kRedataChunk = 8192;
constexpr std::size_t kWaveBands = 32;
#else
constexpr std::size_t kDieSlots = 256;
constexpr std::size_t kBeltChunk = 1;
constexpr std::size_t kRedataChunk = 512;
constexpr std::size_t kWaveBands = 16;
#endif

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
  const std::size_t chunks = (prog.size() + kBeltChunk - 1) / kBeltChunk;
  for (std::size_t ci = 0; ci < chunks; ++ci) {
    const std::size_t base = ci * kBeltChunk;
    const std::size_t end = (base + kBeltChunk < prog.size()) ? base + kBeltChunk : prog.size();
    for (std::size_t pi = base; pi < end; ++pi) {
      const FieldInsn& in = prog[pi];
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
}

}  // namespace

int main() {
  std::array<float, kDieSlots> die{};
  for (std::size_t i = 0; i < kDieSlots; ++i) {
    die[i] = std::sin(static_cast<float>(i) * 0.07f) * 0.5f + 0.25f;
  }

  std::vector<FieldInsn> prog;
  prog.reserve(512);
  for (int i = 0; i < 512; ++i) {
    const auto op = static_cast<Op>(i % 6);
    prog.push_back({op, static_cast<std::uint8_t>(i), static_cast<std::uint8_t>(i * 3),
                    static_cast<std::uint8_t>(i * 7)});
  }

  std::vector<float> weights(kDieSlots, 0.01f);
  std::vector<float> signals(kDieSlots, 0.f);
  for (std::size_t i = 0; i < kDieSlots; ++i) {
    weights[i] += static_cast<float>(i % 11) * 0.001f;
  }

  const auto t0 = std::chrono::steady_clock::now();
  constexpr int frames = 240;
  volatile float sink = 0.f;
#if defined(GROK16_BELT_2_0)
  constexpr int kBeltFrameChunk = 8;
  for (int f0 = 0; f0 < frames; f0 += kBeltFrameChunk) {
    const int fend = (f0 + kBeltFrameChunk < frames) ? f0 + kBeltFrameChunk : frames;
    for (int f = f0; f < fend; ++f) {
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
#else
  for (int f = 0; f < frames; ++f) {
    fieldx86_run(prog, die);
    for (std::size_t b = 0; b < kWaveBands; ++b) {
      die[b] = wave_phase_decouple(die[b], die[(b + 1) % kDieSlots], static_cast<int>(b));
    }
    for (std::size_t i = 0; i < kDieSlots; ++i) {
      signals[i] = die[i] * entropy_fold(die[i], die[(i + 17) % kDieSlots]);
    }
    sink += nexus_score(weights, signals);
  }
#endif
  const auto t1 = std::chrono::steady_clock::now();
  const auto ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

  std::cout << "grok16_field_bench profile=" << kProfile
            << " std=gnu++26 __cplusplus=" << __cplusplus
            << " frames=" << frames << " prog_ops=" << prog.size()
            << " die_slots=" << kDieSlots
            << " belt_chunk=" << kBeltChunk
            << " redata_chunk=" << kRedataChunk
            << " wall_ms=" << ms
            << " nexus_checksum=" << sink << '\n';
  return ms > 0.0 ? 0 : 1;
}