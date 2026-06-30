# Grok16 field rewrite patches (GCC)

Grok16 **is** the G16 field rewrite. It does **not** use upstream `releases/gcc-16`.

## Strategy

1. Clone **`releases/gcc-15`** into `vendor/gcc` (~1.6 GB, local only)
2. Apply field version: `gcc/BASE-VER` → `16.0.0`
3. Configure with `--program-transform-name` → `g16`, `g++16`, `g16-*`
4. `--with-pkgversion=Grok16-16.0.0`
5. Self-host rebuild installs into Grok16 repo root (`G16_PREFIX`)

| Patch | Purpose |
|-------|---------|
| `gcc-base-ver-16.0.0.patch` | Documents `15.3.1` → `16.0.0` on `gcc/BASE-VER` |

The forge also writes `BASE-VER` at configure time; the patch is the reviewed delta.

## Whole tree layout

```
Grok16/
  vendor/gcc/      ← releases/gcc-15 + field BASE-VER (gitignored on GitHub)
  build/gcc/       ← configured make tree (gitignored)
  bin/ lib/ …      ← installed g16/g++16 prefix (gitignored)
  forge/           ← build orchestrator (in git)
  patches/         ← documented deltas (in git)
  scripts/         ← toolchain + consolidate (in git)
```

Upstream: https://gcc.gnu.org/git/gcc.git — branch **`releases/gcc-15`**