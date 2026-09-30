#!/usr/bin/env python3
"""
checker/verify.py

The verification layer -- this is the part that turns "a fuzzer ran" into
"we have proof the exercise objective was met". It independently re-runs
every saved candidate crash against a *fresh* invocation of the target,
so it never just trusts the fuzzer's own claim.

This is deliberately the same instinct as the evaluation suite pattern:
don't assume something worked, build a separate way to check.

Usage: python3 verify.py --target ../target/lookup --crashes-dir ../fuzzer/crashes
"""
import argparse
import glob
import os
import subprocess
import sys


def confirm_crash(target: str, input_path: str, timeout: float = 1.0) -> bool:
    with open(input_path, "r") as f:
        data = f.read()
    try:
        proc = subprocess.run([target], input=data.encode(), capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False
    # Negative returncode == killed by signal (e.g. -11 == SIGSEGV)
    return isinstance(proc.returncode, int) and proc.returncode < 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--crashes-dir", required=True)
    args = parser.parse_args()

    candidates = sorted(glob.glob(os.path.join(args.crashes_dir, "*.txt")))
    if not candidates:
        print("FAIL: no candidate crash files found -- did the fuzzer run?")
        sys.exit(1)

    confirmed = 0
    for path in candidates:
        if confirm_crash(args.target, path):
            confirmed += 1

    print(f"Checked {len(candidates)} candidate input(s); {confirmed} independently confirmed as real crashes.")
    if confirmed > 0:
        print("PASS: exercise objective met (at least one genuine crash found and independently verified).")
        sys.exit(0)
    else:
        print("FAIL: none of the saved candidates reproduced a crash on re-run.")
        sys.exit(1)


if __name__ == "__main__":
    main()
