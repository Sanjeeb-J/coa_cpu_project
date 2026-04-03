#include <stdio.h>
#include <stdlib.h>

#define SIZE 64

int A[SIZE][SIZE];
int B[SIZE][SIZE];
int C[SIZE][SIZE];

void init_matrices() {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            A[i][j] = i + j;
            B[i][j] = i - j;
            C[i][j] = 0;
        }
    }
}

void multiply() {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            for (int k = 0; k < SIZE; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    printf("Starting Matrix Multiplication...\n");
    init_matrices();
    multiply();
    
    // Prevent optimization from removing the calculation
    int sum = 0;
    for (int i = 0; i < SIZE; i++) {
        sum += C[i][i];
    }
    printf("Matrix Multiplication complete. Checksum: %d\n", sum);
    return 0;
}
