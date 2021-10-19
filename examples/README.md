# Examples
File must be formatted with the PC value (in binary, of any bit length) and its actual direction (T or NT) on the same line, separated by a whitespace.
- `example.txt`: General example of format
- `agree_example.txt`: Example of a case where agree predictors are more accurate than saturating counters. 
    - Choose PC indexing method (for simplicity) and set index to bits 1-3.
    - The instructions with PC = 10000010 and PC = 10100010 share the same BHT entry, but have opposite patterns (one is mostly taken, the other is mostly not taken). Misprediction rate is reduced for both instructions when using agree predictors compared to using saturating counters.
