#define SIZE_INPUT 240
#define SIZE_LAYER_1 64
#define SIZE_LAYER_2 64
#define SIZE_LAYER_3 9
#define SIZE_OUTPUT 9


void accelerate_MLP(int input[SIZE_INPUT], int output[SIZE_OUTPUT]) {
#pragma HLS INTERFACE ap_ctrl_none port = return
#pragma HLS INTERFACE s_axilite port = input
#pragma HLS INTERFACE s_axilite port = output

	// Set all bias to 0 for testing
	int bias_layer_1[SIZE_LAYER_1] = {0};
	int bias_layer_2[SIZE_LAYER_2] = {0};
	int bias_layer_3[SIZE_LAYER_3] = {0};

	int weights_layer_1[SIZE_LAYER_1][SIZE_INPUT] = {0};
	int weights_layer_2[SIZE_LAYER_2][SIZE_LAYER_1] = {0};
	int weights_layer_3[SIZE_LAYER_3][SIZE_LAYER_2] = {0};

	int output_layer_1[SIZE_LAYER_1] = {0};
	int output_layer_2[SIZE_LAYER_2] = {0};

	int i, j, sum;

	// Initialize all weights to 1 for testing
	for (i = 0; i < SIZE_LAYER_1; i++) {
		for (int j = 0; j < SIZE_INPUT; j++) {
			weights_layer_1[i][j] = 1;
		}
	}

	for (i = 0; i < SIZE_LAYER_2; i++) {
		for (j = 0; j < SIZE_LAYER_1; j++) {
			weights_layer_2[i][j] = 1;
		}
	}

	for (i = 0; i < SIZE_LAYER_3; i++) {
		for (j = 0; j < SIZE_LAYER_2; j++) {
			weights_layer_3[i][j] = 1;
		}
	}

	// Fully connected layer 1
	for (i = 0; i < SIZE_LAYER_1; i++) {
		sum = 0;
		for (j = 0; j < SIZE_INPUT; j++) {
			sum += input[j] * weights_layer_1[i][j];
		}
		//ReLU activation function
		if (sum < 0) {
			output_layer_1[i] = 0;
		} else {
			output_layer_1[i] = sum + bias_layer_1[i];
		}

	}


	// Fully connected layer 2
	for (i = 0; i < SIZE_LAYER_2; i++) {
		sum = 0;
		for (j = 0; j < SIZE_LAYER_1; j++) {
			sum += output_layer_1[j] * weights_layer_2[i][j];
		}
		//ReLU activation function
		if (sum < 0) {
			output_layer_2[i] = 0;
		} else {
			output_layer_2[i] = sum + bias_layer_2[i];
		}
	}

	// Fully connected layer 3
	for (i = 0; i < SIZE_LAYER_3; i++) {
		sum = 0;
		for (j = 0; j < SIZE_LAYER_2; j++) {
			sum += output_layer_2[j] * weights_layer_3[i][j];
		}
		output[i] = sum + bias_layer_3[i];
	}

}
