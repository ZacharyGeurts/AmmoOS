// AMOURANTHRTX-style field dispatch kernel (CPU) — gnu++26 + Field macros
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>

#ifndef FIELD_X86_DIE
#define FIELD_X86_DIE 1
#endif
#ifndef FIELD_ENTROPY_DISPATCH
#define FIELD_ENTROPY_DISPATCH 1
#endif

struct FieldThermo {
  std::uint32_t entropy_micro{};
  std::uint32_t phi_micro{};
  std::uint32_t wave_speed_micro{};
};

inline FieldThermo dispatch_frame(float entropy, float boundary_thermo, float wave_speed) {
  constexpr float kEntropy = 0.618f;
  FieldThermo t{};
  t.entropy_micro = static_cast<std::uint32_t>(entropy * 1'000'000.f);
  t.phi_micro = 618'000u;
  t.wave_speed_micro = static_cast<std::uint32_t>(wave_speed * 1'000.f);
  const float budget = boundary_thermo - entropy * kEntropy;
  (void)budget;
  return t;
}

int main() {
  std::array<float, 256> canvas{};
  for (std::size_t i = 0; i < canvas.size(); ++i) {
    canvas[i] = std::sin(static_cast<float>(i) * 0.11f);
  }
  FieldThermo acc{};
  for (int frame = 0; frame < 120; ++frame) {
    const float entropy = canvas[static_cast<std::size_t>(frame) % canvas.size()];
    acc = dispatch_frame(entropy, 1.0f, 1420.f);
  }
  std::cout << "field_canvas_kernel entropy_micro=" << acc.entropy_micro
            << " phi_micro=" << acc.phi_micro
            << " wave_speed_micro=" << acc.wave_speed_micro
            << " FIELD_X86_DIE=" << FIELD_X86_DIE << '\n';
  return 0;
}