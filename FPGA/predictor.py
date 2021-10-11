from pynq import Overlay
import struct
import pynq


class Predictor():

    def __init__(self):
        # Initialize pynq Overlay to program FPGA using bitstream
        self.overlay = Overlay('MLP.bit')
        self.accelerate_mlp = self.overlay.accelerate_MLP_0
        self.DANCE_TO_NUM_MAP = {0: 'dab', 1: 'jamesbond', 2: 'mermaid'}

    # Axilite MMIO interface does not support read/write of floats
    def float_to_integer(self, f):
        return struct.unpack('<I', struct.pack('<f', f))[0]

    def integer_to_float(self, i):
        return struct.unpack('f', struct.pack('I', i))[0]

    def predict(self, inputs):

        # Mapping for MMIO obtained from Vivado HLS

        # AXILiteS
        # 0x0000 : Control signals
        #          bit 0  - ap_start (Read/Write/COH)
        #          bit 1  - ap_done (Read/COR)
        #          bit 2  - ap_idle (Read)
        #          bit 3  - ap_ready (Read)
        #          bit 7  - auto_restart (Read/Write)
        #          others - reserved
        # 0x0800 ~
        # 0x0fff : Memory 'inputs' (480 * 32b)
        #          Word n : bit [31:0] - inputs[n]
        # 0x1000 ~
        # 0x100f : Memory 'outputs' (3 * 32b)
        #          Word n : bit [31:0] - outputs[n]
        #          Word n : bit [31:0] - output_r[n]

        INPUT_OFFSET = 0x1000
        OUTPUT_OFFSET = 0x2000
        CONTROL_OFFSET = 0x0000
        AP_START = 1
        AP_DONE = 2
        # Each input is 32 bits = 4 bytes
        NUM_BYTES = 4
        INPUT_LENGTH = 480
        OUTPUT_LENGTH = 3

        # Write input values to IP
        for i in range(INPUT_LENGTH):
            int_input = self.float_to_integer(inputs[i])
            self.accelerate_mlp.write(INPUT_OFFSET + i*NUM_BYTES, int_input)

        # Start executing IP
        self.accelerate_mlp.write(CONTROL_OFFSET, AP_START)

        # Wait for AP_DONE bit to be asserted when outputs are ready
        while self.accelerate_mlp.read(CONTROL_OFFSET) & AP_DONE == 0:
            continue

        # Read output values from IP
        result = []
        for i in range(OUTPUT_LENGTH):
            res = self.accelerate_mlp.read(OUTPUT_OFFSET + i*NUM_BYTES)
            result.append(self.integer_to_float(res))

        # Return label with highest value
        return DANCE_TO_NUM_MAP[result.index(max(result))]
