/* Field execution — C plane (timed kernel, same shape as speed_demo.cpp). */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef TOOLCHAIN_TAG
#define TOOLCHAIN_TAG "c_unknown"
#endif

enum { K_DIE = 256, K_WAVE = 16, K_FRAMES = 240, K_PROG = 512 };
static const float K_PHI = 0.6180339887f;

typedef struct {
  uint8_t op, dst, src, imm;
} FieldInsn;

static int target_seconds(void) {
  const char* env = getenv("SPEED_DEMO_TARGET_SEC");
  if (env) {
    int v = atoi(env);
    if (v > 0 && v <= 600) return v;
  }
  return 10;
}

static float entropy_fold(float e, float thermo) {
  float x = e * K_PHI + thermo * (1.f - K_PHI);
  for (int i = 0; i < 4; ++i)
    x = fmaf(x, 1.113f, sinf(x * 3.14159f) * 0.01f);
  return x;
}

static float wave_phase(float phase, float speed, int band) {
  float w = speed * (float)(band + 1) * 0.001f;
  return fmaf(cosf(phase * w), K_PHI, sinf(phase * (1.f - K_PHI)) * 0.05f);
}

static float nexus_score(const float* w, const float* s, size_t n) {
  float score = 0.f;
  for (size_t i = 0; i < n; ++i) score = fmaf(w[i], s[i], score);
  return score / (float)n;
}

static void fieldx86_run(const FieldInsn* prog, size_t nprog, float* die) {
  for (size_t pi = 0; pi < nprog; ++pi) {
    const FieldInsn* in = &prog[pi];
    size_t d = in->dst % K_DIE, s = in->src % K_DIE, im = in->imm % K_DIE;
    switch (in->op % 6) {
      case 0: die[d] += die[s]; break;
      case 1: die[d] *= die[im] * 0.01f + 1.f; break;
      case 2: die[d] += (float)(in->imm ^ in->src) * 1e-4f; break;
      case 3: die[d] = entropy_fold(die[s], die[im]); break;
      case 4: die[d] = wave_phase(die[s], die[im], (int)(in->imm % K_WAVE)); break;
      default: break;
    }
  }
}

static void run_epoch(const FieldInsn* prog, float* die, float* weights, float* signals, float* sink) {
  for (int f = 0; f < K_FRAMES; ++f) {
    fieldx86_run(prog, K_PROG, die);
    for (int b = 0; b < K_WAVE; ++b)
      die[b] = wave_phase(die[b], die[(b + 1) % K_DIE], b);
    for (int i = 0; i < K_DIE; ++i)
      signals[i] = die[i] * entropy_fold(die[i], die[(i + 17) % K_DIE]);
    *sink += nexus_score(weights, signals, K_DIE);
  }
}

int main(void) {
  const int target_sec = target_seconds();
  float die[K_DIE], weights[K_DIE], signals[K_DIE];
  FieldInsn prog[K_PROG];
  for (int i = 0; i < K_DIE; ++i) {
    die[i] = sinf((float)i * 0.07f) * 0.5f + 0.25f;
    weights[i] = 0.01f + (float)(i % 11) * 0.001f;
    signals[i] = 0.f;
  }
  for (int i = 0; i < K_PROG; ++i) {
    prog[i].op = (uint8_t)(i % 6);
    prog[i].dst = (uint8_t)i;
    prog[i].src = (uint8_t)(i * 3);
    prog[i].imm = (uint8_t)(i * 7);
  }

  struct timespec t0, t1, now, last_tick;
  clock_gettime(CLOCK_MONOTONIC, &t0);
  last_tick = t0;
  int epochs = 0;
  float sink = 0.f;

  while (1) {
    run_epoch(prog, die, weights, signals, &sink);
    ++epochs;
    clock_gettime(CLOCK_MONOTONIC, &now);
    double elapsed = (now.tv_sec - t0.tv_sec) + (now.tv_nsec - t0.tv_nsec) / 1e9;
    if (elapsed >= target_sec) break;
    double since = (now.tv_sec - last_tick.tv_sec) + (now.tv_nsec - last_tick.tv_nsec) / 1e9;
    if (since >= 1.0) {
      int pct = (int)((elapsed / target_sec) * 100.0);
      uint64_t total_ops = (uint64_t)epochs * K_FRAMES * K_PROG;
      fprintf(stderr,
              "SPEED_DEMO_PROGRESS toolchain=%s elapsed_sec=%d target_sec=%d pct=%d epochs=%d total_ops=%llu\n",
              TOOLCHAIN_TAG, (int)elapsed, target_sec, pct, epochs, (unsigned long long)total_ops);
      last_tick = now;
    }
  }

  clock_gettime(CLOCK_MONOTONIC, &t1);
  double wall_ms = (t1.tv_sec - t0.tv_sec) * 1000.0 + (t1.tv_nsec - t0.tv_nsec) / 1e6;
  uint64_t total_ops = (uint64_t)epochs * K_FRAMES * K_PROG;
  double ops_per_sec = total_ops / (wall_ms / 1000.0);

  printf("speed_demo toolchain=%s target_sec=%d wall_ms=%.2f epochs=%d frames_per_epoch=%d "
         "prog_ops=%d total_ops=%llu ops_per_sec=%.2f checksum=%f\n",
         TOOLCHAIN_TAG, target_sec, wall_ms, epochs, K_FRAMES, K_PROG,
         (unsigned long long)total_ops, ops_per_sec, sink);
  return 0;
}