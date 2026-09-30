#!/usr/bin/env python3
"""
fuzzer/fuzz.py

A deliberately simple mutation-based fuzzer. It has no knowledge of the
target's source code -- it only sees "did this input make the program
crash?" This is intentionally close to a minimal, honest version of what
real fuzzers do, just without the coverage-guided sophistication of
something like AFL (or Redqueen).

Usage: python3 fuzz.py --target ../target/lookup --iterations 2000
"""
import argparse
import os
import random
import subprocess
import sys

SEED_CORPUS = ["0 0", "1 5", "3 9", "7 1"]


def mutate(seed: str) -> str:
    """Produce one mutated input from a seed string."""
    choice = random.random()
    if choice < 0.4:
        # Push the index toward large / negative / out-of-range values.
        wild_index = random.choice(
            [
                random.randint(8, 10_000),
                random.randint(-10_000, -1),
                2**31 - 1,
                -(2**31),
            ]
        )
        return f"{wild_index} {random.randint(-100, 100)}"
    elif choice < 0.7:
        # Flip random characters in the seed.
        chars = list(seed)
        if chars:
            i = random.randrange(len(chars))
            chars[i] = random.choice("0123456789 -")
        return "".join(chars)
    else:
        # Pure random garbage.
        return "".join(random.choice("0123456789 -abc\n") for _ in range(random.randint(1, 12)))


def run_target(target: str, data: str, timeout: float = 1.0):
    try:
        proc = subprocess.run(
            [target],
            input=data.encode(),
            capture_output=True,
            timeout=timeout,
        )
        return proc.returncode
    except subprocess.TimeoutExpired:
        return "timeout"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="path to compiled target binary")
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--out", default="crashes", help="directory to save crashing inputs")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed, for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    os.makedirs(args.out, exist_ok=True)

    corpus = list(SEED_CORPUS)
    crashes_found = 0

    for i in range(args.iterations):
        seed = random.choice(corpus)
        candidate = mutate(seed)
        rc = run_target(args.target, candidate)

        # A negative returncode from subprocess means the process was
        # killed by a signal (e.g. -11 for SIGSEGV on Linux).
        if isinstance(rc, int) and rc < 0:
            crashes_found += 1
            fname = os.path.join(args.out, f"crash_{crashes_found:03d}.txt")
            with open(fname, "w") as f:
                f.write(candidate)
            print(f"[!] crash #{crashes_found} (signal {-rc}) saved to {fname}: {candidate!r}")
        elif candidate not in corpus and len(corpus) < 50:
            # Keep the corpus small and cheap; this is not coverage-guided,
            # just enough diversity to keep mutating from varied starting points.
            corpus.append(candidate)

    print(f"\nDone. {args.iterations} iterations, {crashes_found} crash(es) found.")
    sys.exit(0 if crashes_found > 0 else 1)


if __name__ == "__main__":
    main()
