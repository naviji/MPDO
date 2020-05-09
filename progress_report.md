# Problem Statement
Planning the motion of a robot in a square grid with moving obstacles by using Z3 solver.

# Solution Approach

We abstract the problem into finding the intersection of 
boundaries between obstacles and robots to avoid collision.

Each robot and obstacle in the workspace has a surrounding set of grid points that it can move to.The goal of the robot is to find a path to the destination such that these regions does not intersect. 

The robot does not need to consider obstacles outside its range of motion. It makes a plan to the destination considering its immediate neighbourhood and assumes that all other grid points are free.

On each step it checks whether its next step falls in the immediate neighbourhood of an obstacle. If there is no intersection then the robot continues on the pre-calculated path. Else, the path is recalculated marking the grid point as unreachable for the next step.

In the case that the current set of constraints cannot be satisfied the robot stays in the current position till the obstacle moves out of the way.

The current premitive version of a solution that we achieved considers only one robot and one obstacle both occupying one grid point each. We consider only the 5 basic motion primitives, namely up, down, left, right and no movement.

![workspace](/workspace.png)

# Future Concerns 
The concept of a optimal path does not exist if we do not consider the future position of the robot. But considering the future to make a plan also makes no sense. Therefore we are unsure in which direction to continue.
