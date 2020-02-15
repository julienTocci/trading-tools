from globals import *
from percent_change import percent_change


def pattern_storage(average_line: list, pattern_array: list, performance_array: list):
    # Get the length of the array
    # We doubled the dots for pattern =>  we shall not compute (dots_for_pattern) before the end as
    # we will not be able to have (dots_for_pattern) more data after that to verify the real outcome
    x = len(average_line) - (2* dots_for_pattern)

    y = 1 + dots_for_pattern

    # Iterating over all points of the data[:endpoint] and computing for each a comparative array using the next dots_for_pattern points
    while y < x:
        pattern = []

        # Creating the pattern percentage (e.g: len([0.1%, 04%, 5% ...]) = 30
        # First loop:
        # percent_change( average_line[1],average_line[2])
        # Second loop :
        # percent_change( average_line[1],average_line[3]) etc...
        #
        # The while is:
        # First loop:
        # percent_change( average_line[36939],average_line[36940])
        # Second loop :
        # percent_change( average_line[1],average_line[3]) etc...
        for index in reversed(range(dots_for_pattern)):
            point = percent_change(average_line[y - dots_for_pattern], average_line[y - index])
            pattern.append(point)

        # Create the pattern array and store it
        # Will contains a large number of pattern arrays (len(average_line) - dots_for_pattern +1)
        pattern_array.append(pattern)

        # Take the range of the outcome using 10 values from the 20th after the current point
        # The outcome range are basically the last 10 values of the next (dots_for_pattern) points
        outcome_range = average_line[y+dots_for_pattern-10:y+dots_for_pattern]

        # Take the current point
        current_point = average_line[y]

        # Get the average value of the outcome
        try:
            average_outcome = np.average(outcome_range)
        except Exception as e:
            print(e)
            average_outcome = 0

        # Get the future outcome for the pattern based on the average outcome value
        # Will be in % the change between the current point and the average of the last values of the next (dots_for_pattern) slots
        future_outcome = percent_change(current_point, average_outcome)

        # Store the outcome value
        # e.g: -0,7%
        performance_array.append(future_outcome)

        y += 1
