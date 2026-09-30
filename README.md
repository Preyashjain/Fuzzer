# Fuzzing Exercise

This is a small exercise for learning the first useful step in fuzzing: finding out whether a program crashes on unexpected input.

The target program has a deliberately unchecked array index. The fuzzer generates inputs and saves the ones that make the target crash. The checker then runs those inputs again in separate target processes, so a result only counts when it can be reproduced.

This stops at crash discovery. It does not include payloads, shellcode, or an attempt to turn the bug into code execution.

## Structure

```
target/     the deliberately buggy program (an unchecked array index)
fuzzer/     a basic mutation fuzzer that discovers the crash
checker/    independently re-runs candidate crashes to confirm they are real
Dockerfile  the reproducible environment for all of the above
```

## A few design choices

- The target is intentionally small, so it is easy to see why an input crashes.
- The checker does not trust the fuzzer's output. It opens each saved input and starts the target again.
- Docker keeps the compiler, scripts, and commands in one place. That makes the exercise easier to run on another machine.

## Run it with Docker

```bash
docker build -t fuzzing-exercise .
docker run --rm fuzzing-exercise
```

## Run it without Docker

```bash
gcc -O0 -fno-stack-protector -o target/lookup target/lookup.c
python3 fuzzer/fuzz.py --target target/lookup --iterations 2000 --seed 42 --out fuzzer/crashes
python3 checker/verify.py --target target/lookup --crashes-dir fuzzer/crashes
```

The last command is the important one: it independently checks the files saved by the fuzzer and reports how many reproduce a crash.
