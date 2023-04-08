# Five Sigma Technical Assesment
---

There are 3 problems (labelled A, B & C) in this exercise.

Problems A&B are algorithmic puzzles, and pure python code (i.e. avoiding use of numpy/pandas and only using
python’s inbuilt data structures) is preferred for these. Problem C is a data analysis task and use of pandas 
is expected for this task. If you want to do any plotting please use whatever library you are most comfortable with.
Responses are mainly judged on code simplicity & readability. Feel free to add comments to your code where you
think appropriate but there is no need to document every line. Don’t be concerned if you cannot solve all the 
problems and please submit what you do complete. Please write a separate script (.py file) for each problem. 
If possible a jupyter notebook (.ipynb file) is preferred for problem C if you are used to using jupyter.


## Problem A

At a concert, there are 100 seats numbered 1-100 and 100 tickets also numbered 1-100. Due to social distancing 
measures, members of the audience are only allowed in one at a time, in ticket order starting from ticket 1, 
and must sit in the seat with the same number as is on their ticket. However the first member of the audience 
has had a few too many drinks and sits in a random seat. Further audience members will sit in the seat on their 
ticket if it is free, but if it is taken they will panic and also sit in a random seat

1. Write a function to simulate audience members taking their seats

2. Use monte carlo simulation to measure the probability (from e.g. 1000 simulations) that the person with the 
last ticket (ticket 100) gets to sit in their own seat (seat 100).  (The true probability is 0.5 so make sure
your implementation matches up!)

3. For when we have our follow-up discussion/interview: think about the computational complexity of your
implementation (i.e. big O notation). Can you think of any alternative algorithms that would significantly
reduce computational complexity? No additional code is needed for this step.


## Problem B
For this problem there are 2 files provided that each contain a 2D map. In each file characters “ *\~” 
represent squares in the map that contain either a field (space character), flower (*) or caterpillar (~). New
line characters indicate the start of a new row (y-axis) in the map. Use Classes to implement the behaviours 
of each field, flower and caterpillar, and run a simulation according to the following rules:

- A field will become a flower if three or more adjacent squares contain flowers. Otherwise, nothing
happens.

- If a flower is surrounded by three or more caterpillars, the flower will get eaten and a new caterpillar 
will replace the flower. Otherwise, nothing happens

- If a caterpillar is next to at least one other caterpillar and at least one flower, it won't get too
lonely or hungry and survives (i.e. nothing happens), otherwise the caterpillar dies and the square becomes a field.

- In the above, adjacent squares are the 9 squares that are next to the square under consideration
(i.e. including diagonals)

- These changes happen across all squares in the map simultaneously in each time step. Only one change 
(e.g. field to flower, flower to caterpillar, or caterpillar to field) can occur within a square
each time step.

Keep track of a “score”, calculated as follows at the end of each time step:

- For every flower, add the number of time steps that flower has survived for to the score
- For every caterpillar, subtract one from the score

Simulate until either:

1. there are no further changes to the map – in which case count the number of steps that
occurred or

2. the map enters an infinite loop – in which case determine the number of iterations in a single
loop

Sense check your program: the first file will reach a stable endpoint within ~20 iterations, the second will
enter an infinite loop approx 35 iterations long

Alter your program to optionally (if a certain flag is set) generate butterflies:
- Instead of caterpillars always dying, there is a 1/100 chance that a caterpillar will turn into a butterfly 
who can move around the map, starting from the current square

- If a butterfly is created, the caterpillar square still turns into a field

Each time step, after the usual rules have been applied and butterfly creation has occurred, butterflies behave 
as follows:
 If the square the butterfly is on contains a flower, the butterfly eats it, reproduces and
dies, turning the square into a caterpillar
 Otherwise:
 there is a 1/10 chance that the butterfly dies
 if the butterfly survives, it moves randomly on the x-axis by -1,0,1 steps and
randomly on the yaxis by -1,0,1 steps

 The randomness introduced by butterflies can make simulation of the larger map run without
entering an infinite loop or with gradually changing behaviour over time. If you have
time/inclination, animate the output via console/jupyter/method of your choice, drawing
butterflies on top of the map using character “B”, and enjoy :)

Problem C
 The file “Problem C data.xlsx” contains example data on a portfolio of loans as of a specific date (in this
case 1 July 2022). Each row in the file corresponds to a loan and each column records information about
that loan as of 1 July 2022.
1. The file contains 4 types of data errors that we have introduced into it. While working through the
questions below, can you find these errors?
2. Produce a few stratifications of the data to help understand the composition of the portfolio.
Do this by charting/tabulating the % composition (measured by % of the total of the column “Remaining
capital”), when grouped by each the following columns.
1. “October Rating”
2. “Initial duration” – bucket this into a small number of categories first
3. “Country”
4. “Annual Rate” – bucket this into a small number of categories first
5. “Status”
3. Produce a table summarising the average of the “Annual Rate” when grouping the data into groups by
both “October Rating” and “Initial duration”.
1. Please do this by producing a “multi-factor” grouping i.e. “October Rating” in the row headings and
“Initial duration” in the column headings
2. When calculating the average “Annual Rate”, please calculate a weighted average, using “Remaining
capital” for the weights.
