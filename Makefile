CC = gcc
CFLAGS = -static -O2

all: matrix_mult branch_heavy memory_stride

matrix_mult: matrix_mult.c
	$(CC) $(CFLAGS) -o matrix_mult matrix_mult.c

branch_heavy: branch_heavy.c
	$(CC) $(CFLAGS) -o branch_heavy branch_heavy.c

memory_stride: memory_stride.c
	$(CC) $(CFLAGS) -o memory_stride memory_stride.c

clean:
	rm -f matrix_mult branch_heavy memory_stride
