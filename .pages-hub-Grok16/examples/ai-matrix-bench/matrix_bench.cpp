// Field/AI matrix micro-benchmark for grok16-toolchain.sh bench
#include <chrono>
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <vector>

#if defined(GROK16_PROFILE_FIELD_OPT)
constexpr const char* kProfile = "field_opt";
#elif defined(GROK16_PROFILE_AI)
constexpr const char* kProfile = "ai";
#elif defined(GROK16_PROFILE_FIELD)
constexpr const char* kProfile = "field_compute";
#elif defined(GROK16_PROFILE_VULKAN)
constexpr const char* kProfile = "vulkan_rtx";
#else
constexpr const char* kProfile = "default";
#endif

static void matmul(const std::vector<float>& a, const std::vector<float>& b,
                   std::vector<float>& c, std::size_t n) {
  for (std::size_t i = 0; i < n; ++i) {
    for (std::size_t j = 0; j < n; ++j) {
      float sum = 0.f;
      for (std::size_t k = 0; k < n; ++k) {
        sum += a[i * n + k] * b[k * n + j];
      }
      c[i * n + j] = sum;
    }
  }
}

int main() {
  constexpr std::size_t n = 64;
  std::vector<float> a(n * n, 0.01f), b(n * n, 0.02f), c(n * n, 0.f);
  for (std::size_t i = 0; i < n * n; ++i) {
    a[i] += static_cast<float>(i % 17);
    b[i] += static_cast<float>(i % 13);
  }

  const auto t0 = std::chrono::steady_clock::now();
  constexpr int iters = 48;
  volatile float sink = 0.f;
  for (int rep = 0; rep < iters; ++rep) {
    matmul(a, b, c, n);
    sink += c[rep % (n * n)];
  }
  const auto t1 = std::chrono::steady_clock::now();
  const auto ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

  std::cout << "grok16_bench profile=" << kProfile
            << " std=gnu++26 __cplusplus=" << __cplusplus
            << " n=" << n << " iters=" << iters
            << " wall_ms=" << ms
            << " checksum=" << sink << '\n';
  return ms > 0.0 ? 0 : 1;
}