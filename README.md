# Fuzzing Exercise — Crash Discovery Harness (Draft / Proof of Concept)

**What this is.** A small, self-contained, containerized exercise for teaching the *first* step of vulnerability assessment: finding that a bug exists, before ever touching how it might be exploited. A student writes or extends a fuzzer, points it at a deliberately buggy target, and an automated checker independently confirms whether they actually found a real crash.

**What this deliberately is not.** There is no exploitation step here — no shellcode, no payload crafting, no attempt to turn the crash into controlled execution. The target's only job is to be crash-able; the fuzzer's job is to find that; the checker's job is to independently confirm it, not just trust the fuzzer's own report.

## Structure

```
target/    the deliberately buggy program (an unchecked array index)
fuzzer/    a basic mutation fuzzer that discovers the crash
checker/   independently re-runs any candidate crash to confirm it's real
Dockerfile reproducible environment for all of the above
```

## Why built this way

- **Reproducible, not "works on my machine"** — everything runs the same way in the container as anywhere else.
- **The checker never trusts the fuzzer** — it re-executes every candidate input itself before counting it as a real finding. This is the same principle as any evaluation suite: don't assume something worked, build a separate way to verify it.
- **The target is intentionally minimal and generic** — this is a proof of the *harness pattern*, not a finished course exercise. The actual bug class, difficulty curve, and learning objectives are exactly where your input would matter most — this was built to be a starting point for that conversation, not a replacement for it.

## Running it

```bash
docker build -t fuzzing-exercise .
docker run --rm fuzzing-exercise
```

Or without Docker:
```bash
gcc -O0 -fno-stack-protector -o target/lookup target/lookup.c
python3 fuzzer/fuzz.py --target target/lookup --iterations 2000 --seed 42 --out fuzzer/crashes
python3 checker/verify.py --target target/lookup --crashes-dir fuzzer/crashes
```

## Verified working (outside Docker; the container build itself wasn't testable in the environment this was built in)

- Target compiles cleanly; confirmed it crashes on out-of-range input and behaves normally otherwise.
- Fuzzer found 810 independently-reproducing crashes out of 2,000 iterations (seed 42).
- Checker independently re-ran and confirmed all 810 as genuine.
