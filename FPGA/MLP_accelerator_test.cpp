#include <stdio.h>

#define SIZE_INPUT 240
#define SIZE_OUTPUT 9

void accelerate_MLP(int input[SIZE_INPUT], int output[SIZE_OUTPUT]);




int main() {
	int input[SIZE_INPUT] = {0};
	int output[SIZE_OUTPUT] = {0};
	int expected_output[SIZE_OUTPUT] = {0};

	int i, j;
	// Set all input values to 1 for testing
	for (i = 0; i < SIZE_INPUT; i++) {
		input[i] = 1;
	}

	int expected_output_value = 240 * 64 * 64;
	for (i = 0; i < SIZE_OUTPUT; i++) {
		expected_output[i] = expected_output_value;
	}


	accelerate_MLP(input, output);

	/* Compare the data send with the data received */
	printf(" Comparing data ...\r\n");
	for (i = 0; i < SIZE_OUTPUT; i++) {
		if (expected_output[i] != output[i]) {
			printf("Test Failed\r\n");
			return 0;
		}
	}


	printf("Test Success\r\n");

	return 0;
}
