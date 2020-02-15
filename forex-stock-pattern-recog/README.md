# Forex and Stock Python Pattern Recognizer

## Introduction
This project represents a machine learning program that is able to recognize patterns inside Forex or stock data. 

## Requirements 
In order to run the code you need to have the following libraries and programs installed on your computer
* Python 3.6
* `numpy`
* `matplotlib`

wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
python3 -m pip install numpy
python3 -m pip install matplotlib


## How it works 
The program will run the following tasks
1. Take the first `end_point` (inside `settings.py`) lines of data.
2. Create for each point an array of size `dots_for_pattern` describing a pattern after it. Store the pattern
3. use  last  `dots_for_pattern` points of the sliced data as the "current_pattern"
4. Recognize the patterns that are most similar to the new data. This means that
   * Each pattern must be made of points that are at least 50% similar to the corresponding point inside the new data
   * Each pattern must be overall at least `pattern_similarity_value`% similar to the new pattern
5. Save into the `patterns` folder a graph with the following data plotted inside
   * All the patterns that have been recognized, each one with a different color
   * The pattern that was been searched for, in a turquoise and thicker line
   * The predictions of the outcome of all the recognized patterns
      * A green dot for each outcome that represents a prediction of a rise
      * A red dot for each outcome that predicts a fall
   * The average predicted outcome value as a blue dot
   * The real outcome value as a turquoise dot
 6. Increment by one the considered set of data and repat from point (1).

TODO:
Use Yahou Finance historical data as input (example https://fr.finance.yahoo.com/quote/%5EFCHI/history?p=%5EFCHI)
Use day to day data. We need to see trends overs several weeks (dots_for_pattern being 30 would mean pattern over a month)
Find a way to multiThread the computation (way too long as for now) and/or usr machines with more ressources (Cloud)



```
