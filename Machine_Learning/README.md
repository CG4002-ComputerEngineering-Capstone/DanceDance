# MACHINE LEARNING # 

The `Final` folder contains the codebase used to implement a Multi Layer Perceptron model, capable of classifying different dance moves based on real-time sensor readings from accelerometer and gyroscope. This was used during the Week 13 evaluation of CG4002 Capstone Project. 

| FileName | Description |
| --- | --- |
| `Final/finaleLive.py` | Live data handler script used to preprocess and generate input vector to be passed into the neural network for prediction |
| `Final/loadData.py` | Loads data from `capstone_data` folder to generate training and test dataframes |
| `Final/preprocess.py` | Pre-processing script to generate input vector for the nn model from training and test dataframes |
| `Final/utility.py` | Helper functions for visualisation |
|`Final/nn_trainer.ipynb`| MLP trainer, used to train, validate, test and evaluate the model |
|`Final/mlp.csv`| Saved MLP weights which were passed for Hardware acceleration on the Ultra96 |
| `capstone_data` | Data collected from team for various dance moves. Naming convention : `<subjectName_danceMove_trialNum.csv>` |
| `Week_9_Prep` | Codebase for Week 9 evaluation |
| `Week_11_Prep` | Codebase for Week 11 evaluation |


