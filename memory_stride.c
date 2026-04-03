#include <stdio.h>
#include <stdlib.h>

#define ARR_SIZE (1024 * 1024 * 2) // 2 MB array (larger than most L1 caches)
#define STRIDE 1024                 // Jump by large amounts to cause cache misses
#define ITERS 2

int arr[ARR_SIZE];

int main() {
    printf("Starting Memory Stride...\n");
    
    for (int i = 0; i < ARR_SIZE; i++) {
        arr[i] = i;
    }

    long long sum = 0;
    for (int iter = 0; iter < ITERS; iter++) {
        for (int i = 0; i < ARR_SIZE; i += STRIDE) {
            sum += arr[i];
            arr[i] = sum % 100; // write back to invalidate cache lines
        }
    }
    
    printf("Memory Stride complete. Sum: %lld\n", sum);
    return 0;
}
