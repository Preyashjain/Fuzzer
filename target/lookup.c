/*
 * target/lookup.c
 *
 * A deliberately simple, deliberately buggy program, written ONLY as a
 * teaching target for a crash-discovery (fuzzing) exercise.
 *
 * What it does: reads a single line from stdin of the form "INDEX VALUE",
 * and stores VALUE into a small fixed-size lookup table at position INDEX.
 *
 * The bug: INDEX is never checked against the bounds of the array before
 * it's used. A student's fuzzer should be able to find this by trying
 * enough inputs and noticing the program crashes.
 *
 * This program has NO exploitation payload, no shellcode, and does not
 * demonstrate turning the crash into controlled execution -- it exists
 * purely to be crashed and have that crash reported, which is the first,
 * defensive step in vulnerability assessment (finding that a bug exists),
 * not the offensive step (weaponizing it).
 */
#include <stdio.h>
#include <stdlib.h>

#define TABLE_SIZE 8

int main(void) {
    static int table[TABLE_SIZE];
    int index, value;

    if (scanf("%d %d", &index, &value) != 2) {
        /* Malformed input: exit cleanly, this is not the bug we want found */
        return 0;
    }

    /* BUG: no bounds check on `index` before using it. */
    table[index] = value;

    printf("stored %d at %d\n", value, index);
    return 0;
}
