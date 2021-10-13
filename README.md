# branch-prediction-visualization

Visualize and compare different branch prediction methods using Python and Tkinter GUI.  

Currently only shows branch direction predictions (taken or not taken), not branch target address predictions or branch instruction predictions (determining whether instruction is branch), since these can generally be done efficiently with a branch target buffer (BTB).  

Note that this tool is simply to be used for visualizing and better understanding branch prediction accuracy of different branch prediction methods under different taken / not taken situations, not for rigorous testing for comparison between the methods.  

Branch prediction methods covered:
- Simple (bimodal) n-bit predictors
- Agree predictor (bias bit set based on first direction)


## Possibly to be added
- Indexing into BHT
- Perceptron branch prediction  
- Predictor for predictors (e.g. Alpha 21264 Tournament Predictor)
- More misprediction stats (e.g. input a # of stages to flush for each misprediction, and it'll tell you the slowdown rate compared to perfect prediction)
- Sample T/NT patterns representing loop branches, dependent branches, etc. to show how different methods are better in certain cases.
- Geometric history length predictors? TAGE

Indexing function:  
- PC
- GHR
- GHR XOR PC
Input: list of (PC of branch instruction, T or NT)

## Usage
Make sure Tkinter is installed, and open/run `main.py` with Python 3.X

