#include <stdio.h>
#include <stdlib.h>

#define ITERS 500000

int main() {
    printf("Starting Branch Heavy loop...\n");
    long long sum = 0;
    
    // An unpredictable branch pattern using simple arithmetic
    for (int i = 0; i < ITERS; i++) {
        if ((i % 2 == 0) && (i % 3 != 0) || (i % 7 == 0)) {
            sum += i;
        } else if (i % 5 == 0) {
            sum -= i;
        } else {
            sum += 1;
        }
    }
    
    printf("Branch Heavy complete. Sum: %lld\n", sum);
    return 0;
}
