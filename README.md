# branch-prediction-visualization

Visualize and compare different branch prediction methods using Python and Tkinter GUI.  

Currently only shows branch direction predictions (taken or not taken), not branch target address predictions or branch instruction predictions (determining whether instruction is branch), since these can generally be done efficiently with a branch target buffer (BTB).  

Note that this tool is simply to be used for visualizing and better understanding branch prediction accuracy of different branch prediction methods under different taken / not taken situations, not for rigorous testing for comparison between the methods.  

## Branch prediction methods covered (or in the works)
Compare between simple n-bit saturating counters or simulate custom branch predictor with the following choices:
- BHT entry types
    - n-bit saturating counters
    - n-bit agree predictor (bias bit set based on first direction)
![alt text](assets/bht_entry_choices.png)
- Indexing methods for BHT
    - PC
    - GHR
    - GHR XOR PC (GShare)
    - PHT entry XOR PC (PShare)
![alt text](assets/indexing_choices.png)
- Input: list of (PC of branch instruction, T or NT)


## Possibly to be added

- Perceptron branch prediction  
- Predictor for predictors (e.g. Alpha 21264 Tournament Predictor)
- More misprediction stats (e.g. input a # of stages to flush for each misprediction, and it'll tell you the slowdown rate compared to perfect prediction)
- Sample T/NT patterns representing loop branches, dependent branches, etc. to show how different methods are better in certain cases.
- Geometric history length predictors? TAGE
- n by n predictors? Multiple arrays of predictors, use PC to select index, then use GHR to select array.

## Usage and Dependencies
Make sure Tkinter and pillow are installed, and open/run `main.py` with Python 3.X

## References
Agree predictors:  
Eric Sprangle, Robert S. Chappell, Mitch Alsup, and Yale N. Patt. 1997. The agree predictor: a mechanism for reducing negative branch history interference. SIGARCH Comput. Archit. News 25, 2 (May 1997), 284–291. DOI:https://doi.org/10.1145/384286.264210