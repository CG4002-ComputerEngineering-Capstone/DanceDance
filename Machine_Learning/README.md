# MACHINE LEARNING # 

## Discrete Stochastic Signal Analysis

#### Theory
- Time series data: y = f(t)
- Signal is more general. The independent variable can be t, spatial coordinates, frequency, etc.
    - For e.g. a picture can be seen as a signal which contains information about the brightness of three colors (RGB) across two spatial dimensions.
- Nyquist rate = 2 * highest frequency present in the signal
- A signal is said to be under-sampled if the sampling rate is smaller than the Nyquist rate. 
- Human activity frequencies are between 0 and 20 Hz, and 98% of the FFT amplitude is contained below 10 Hz.

> Any signal can be decomposed into a sum of its simpler signals. These simpler signals are trigonometric functions (sine and cosine waves). 

FFT = time-domain to frequency-domain. 

## Signal processing pipeline 
> Meaurements are done at a constant rate of `20Hz`. After normalisation and filtering out of noise, useful features are extracted from the axial signals. 

### FFT

#### If t_signal is an acceleration signal: 
- t_DC_component is the gravity component [Grav_acc]
- t_body_component is the body's acceleration component [Body_acc]

#### If t_signal is a gyro signal:  
- t_DC_component is not useful [noise]
- t_body_component is the body's angular velocity component [Body_gyro]

#### f_signals: 
- DC_component: f_signal values having freq between  `[-0.3 hz to 0 hz]`  and from  `[0 hz to 0.3hz]`
- body_component: f_signal values having freq between  `[-10 hz to -0.3 hz)`  and from  `(0.3 hz to 10 hz] `


### Segmentation 

> The signals are segmented in fixed-width sliding windows of `2 sec` with an overlap of `50%`. Therefore, each window will have `20 x 2 = 40 samples` in total.

> Each window corresponds to an input vector row. Just by looking at 3-axial acc and 3-axial gyro readings for each sample point in a window, there would be `6 * 40 = 240 cols` in an input vector row. This vector can then be fed into the Multi-Layer Perceptron model for prediction. 
