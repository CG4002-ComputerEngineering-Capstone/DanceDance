# FPGA #

An MLP Neural Network hardware accelerator implemented using C++ in Vivado HLS. An Axilite MMIO interface is used to handle reading and writing of data between Ultra96 CPU and FPGA.


### Files ###

MLP_accelerator.cpp: MLP model implemented in Vivado HLS C++

MLP_accelerator_test.cpp: C++ testbench for simulation

MLP_axilite.ipynb: Jupyter notebook for testing accuracy of FPGA model and recording ultra96 power usage

predictor.py: Pynq driver script to process live data using FPGA and return predicted output 


