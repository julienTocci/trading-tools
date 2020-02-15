import time

from globals import *

from pattern_storage import pattern_storage
from current_pattern import current_pattern
from pattern_recognition import pattern_recognition

total_start = time.time()

# Determines the length of the data
print("Data length:", data_length)

samples = 0
while end_point < data_length:
    average_line = all_data[:end_point]

    pattern_array = []

    # will contains the percentage difference between each points and the average of some points dots_for_pattern-10 later
    # Basically the difference between the point and the value that came a bit after
    performance_array = []
    pattern_for_recognition = []

    # Store the patterns found since now
    # the number of patterns is: len(all_data[:end_points])
    # each patterns is a (dots_for_pattern) array
    pattern_storage(average_line=average_line,
                    pattern_array=pattern_array, performance_array=performance_array)

    # Determine the current pattern based on the last dots_for_pattern data
    # The current pattern is placed at the end_point-dots_for_pattern
    # meaning the first analyzed points are the end_point-dots_for_pattern
    # the points before are just used to create patterns
    # Fill the pattern_for_recognition with the current pattern
    current_pattern(average_line=average_line, pattern_for_recognition=pattern_for_recognition)

    # Perform the pattern recognition
    pattern_recognition(samples=samples,
                        pattern_array=pattern_array, performance_array=performance_array,
                        pattern_for_recognition=pattern_for_recognition)

    # Get one more sample
    samples += 1

    accuracy_average = np.average(accuracy_array)
    print("Backtested accuracy is", str(accuracy_average), "% after ", samples, "samples")

    end_point += 1

total_end = time.time()
print("Script took ", total_end - total_start, " seconds")