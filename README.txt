[NOTE]
this is the coding for vein-based pattern formation in version3.0.

[The key]
1. the comparison on four different ven-based structures.

2. run 36 * 11 trials on four vein-based formation structures to record makespan and average distance.

3. the rectify algorithm
a. full coalition
b. understaffed coalition
# only compensate from the previous coalition
# compensate from the previous and next coalition
# only compensate from the next coalition
c.glut coalition
# only send out to the previous coalition
# send out to the previous and next coalition
# only send out to the next coalition

[The description]
1. Preprocess.py: 
# input: a shape image
# output: a set of dot locations, ROI (min_height,max_height,min_width,max_width)

2. RandomPoints.py:
# input: the number of rows, the number of columns, the number of required dots
# output: the set of randomly distributed locations

3. VeinCoalitions.py
# input: the set of locations, row, col, the typeof vein-based structure
# type=1,slope=0;type=2,slope=pi/2;type=3,slope=pi/4;type=4,slope=3pi/4
# output: a vein-based group of locations

4.formation-VB1.py
# type=1,slope=0,the vein-based formation

5. formation-VB2.py
# type=2,slope=pi/2, the vein-based formation

6.formation-VB3.py
# type=3,slope=pi/4,the vein-based formation

7. formation-VB4.py
# type=4,slope=3pi/4, the vein-based formation




