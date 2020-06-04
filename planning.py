from z3 import Not, Bool, Int, Optimize
from z3 import And, Or, simplify, Implies, sat, unsat
import random
import sys
import time

class Primitive:
    def __init__(self, id, swath, final_x, final_y):
        self.id = id
        self.swath = swath
        self.final_x = final_x
        self.final_y = final_y

    



class Obstacle:
    moves = [(0,0), (1,0), (0,1), (-1,0), (0,-1)]

    def __init__(self, x, y, grid):
        self.x = x
        self.y = y
        self.grid = grid
    
    def next_move(self):
        while (True):
            dx, dy = random.choice(self.moves)
            # dx, dy = (0, 0)
            if ((0 <= self.x+dx < self.grid) and (0 <= self.y+dy < self.grid)):
                self.x += dx
                self.y += dy
                return (self.x, self.y)

# def intersection_points(robot_pos, obs_pos):
#     (rx, ry) = robot_pos
#     (obx, oby) = obs_pos # (a, b)

#     robot_halo = set([(rx, ry), (rx+1, ry), (rx, ry+1), (rx, ry-1), (rx-1,ry)])
#     obs_halo = set([(obx, oby),(obx+1, oby), (obx, oby+1), (obx-1, oby),(obx, oby-1)])
#     return list(robot_halo.intersection(obs_halo))
def next_intersection_points(next_robot_pos, obs_pos):
    (rx, ry) = next_robot_pos
    (obx, oby) = obs_pos # (a, b)

    robot_pos = set([(rx, ry)])
    obs_halo = set([(obx, oby),(obx+1, oby), (obx, oby+1), (obx-1, oby),(obx, oby-1)])
    return list(robot_pos.intersection(obs_halo))

def get_plan(m):
    return sorted([d.name() for d in m.decls() if m[d]==True], key=lambda item: int(item.split('_')[1]))

def get_robot_pos(m,hop):
    (_, _, x, y) = get_plan(m)[hop].split('_') 
    return (int(x), int(y)) 

def path_valid(robot_plan, obs_plan):
    return len([(a, b) for a, b in list(zip(robot_plan, obs_plan)) if a == b]) == 0

def distance(x1, y1, x2, y2):
        return abs(x1-x2) + abs(y1-y2)    

GRID_SZ = 15
HOPS = 28

print("WORKSPACE SIZE (%s x %s)" % (GRID_SZ, GRID_SZ))
print("HOPS ALLOWED = %s" % (HOPS))

def main(args):
    # print(args)
    seed = int(args[0])
    random.seed(seed)


    # New primitive
    primitives = []

    # Stay there
    primitives.append(Primitive(1, [[0,0]], 0, 0))

    # Move right
    primitives.append(Primitive(2, [[0,0], [1,0]], 1, 0))

    # Move left
    primitives.append(Primitive(3, [[0,0], [-1,0]], -1, 0))

    # Move up
    primitives.append(Primitive(4, [[0,0], [0,1]], 0, 1))
    
    # Move down
    primitives.append(Primitive(5, [[0,0], [0,-1]], 0, -1))

    P =  [ Int("p_%s" % (k)) for k in range(HOPS+1) ]
    
    
    # X is a three dimensional grid containing (t, x, y)
    X =  [ [ [ Bool("x_%s_%s_%s" % (k, i, j)) for j in range(GRID_SZ) ]
        for i in range(GRID_SZ) ] 
        for k in range(HOPS+1)]

    s = Optimize()

    # P should be between 1 and 5 for each time step
    s.add([And(1 <= prim , prim <= 5) for prim in P])

    # If primitive id is one of all primitive ids , then make the corresponding swath as true
    for grid in X:
        for i in range(len(grid)):
            for j in range(len(grid)):
                for prim_var in P:
                    for prim_instance in primitives:
                        for s in prim_instance.swath:
                            if ((0 <= i+s[0] < GRID_SZ) and (0 <= j+s[1] < GRID_SZ)):
                                s.add(Implies(prim_var == prim_instance.id, grid[i + s[0]][j + s[1]]))

#if the primitive chosen takes the robot out of the  out of the grid then it should be said that that primitve should not be chosen.

#it could be done the same way as obstacles. We could assert the grid points to be false all througout time
#But this would require the extension of the workspace by one grid point in every direction.

    # After the timestep the position of the robot should be curr + (final_x, final_y)
    for t in range(HOPS):
        for x in range(GRID_SZ):
                for y in range(GRID_SZ):
                    for prim_instance in primitives:
                        s.add(Implies(P[t] == prim_instance.id, X[t+1][x + prim_instance.final_x][y + prim_instance.final_y]))
                        s.add(Implies(X[t+1][x + prim_instance.final_x][y + prim_instance.final_y], P[t] == prim_instance.id))
                        # take this primitive if and only if this final position is reached from the current position.
                        # 




    # Initial Constraints
    s.add(X[0][0][0])
    s.add([Not(cell) for row in X[0] for cell in row][1:])

    # Final constraints
    s.add(X[HOPS][GRID_SZ-1][GRID_SZ-1])
    s.add([Not(cell) for row in X[HOPS] for cell in row][:-1])

    #Sanity Constraints
    for grid in X:
        for i in range(len(grid)):
            for j in range(len(grid)):
                for p in range(len(grid)):
                    for q in range(len(grid)):
                        if not (i==p and j==q):
                            s.add(Not(And(grid[i][j], grid[p][q])))
    
    #Motion primitives
    for t in range(HOPS):
        for x in range(GRID_SZ):
                for y in range(GRID_SZ):
                    temp = Or(X[t][x][y])
                    if (x+1 < GRID_SZ):
                        temp = Or(temp, X[t][x+1][y])
                    if (y+1 < GRID_SZ):
                        temp = Or(temp, X[t][x][y+1])
                    if (x-1 >= 0):
                        temp = Or(temp, X[t][x-1][y])
                    if (y-1 >= 0):
                        temp = Or(temp, X[t][x][y-1])
                    s.add(simplify(Implies(X[t+1][x][y], temp)))


    # # Cost constraints
    # for t in range(HOPS):
    #     for x in range(GRID_SZ):
    #         for y in range(GRID_SZ):
    #             s.add_soft(Not(X[t][x][y]), distance(x, y, GRID_SZ-1, GRID_SZ-1))


    hop = 0
    if s.check() == sat:
        m = s.model()
    else:
        print("No.of hops too low...")
        exit(1)
    obs1 = Obstacle(0, 3, GRID_SZ)

    robot_plan = []
    obs_plan = []
    # for a in s.assertions():
    #     print(a)
    while (hop < HOPS):
        
        robot_pos = (0, 0) if hop == 0 else get_robot_pos(m,hop)
        obs_pos = obs1.next_move()
        
        s.add(X[hop][robot_pos[0]][robot_pos[1]])
        # print("hop is ", hop)
        # print("robot at ", robot_pos)
        # print("obs at ", obs_pos)

        if robot_pos == obs_pos:
            print("COLLISION!!!")
            print(robot_plan)
            print(obs_plan)
            exit()

        robot_plan.append(robot_pos)
        obs_plan.append(obs_pos)
        #next position of the robot
        next_robot_pos = get_robot_pos(m,hop+1)
        s.push()
        # print("intersection points")
        # print(intersection_points(robot_pos, obs_pos))
        # count = 0
        next_overlap = next_intersection_points(next_robot_pos, obs_pos)
        for (x, y) in next_overlap:
            # consider only the intersection with the next step in the plan
            s.add(Not(X[hop+1][x][y]))
        
        if len(next_overlap)>0: # we need to find a new path
            if (s.check() == unsat):
                print("stay there")
            else:
                m = s.model()
                # print("Plan for hop = " + str(hop+1))
                # print(get_plan(m))
                hop += 1
        else:
            # we don't need to worry about the path
            hop += 1

        s.pop()
        
    robot_pos = get_robot_pos(m,hop)
    obs_pos = obs1.next_move()
    # print("hop is ", hop)
    # print("robot at ", robot_pos)
    # print("obs at ", obs_pos)
    robot_plan.append(robot_pos)
    obs_plan.append(obs_pos)

    if path_valid(robot_plan, obs_plan):
        print("PATH IS VALID!!!")
    else:
        print("PATH IS INVALID!!!")
    print("ROBOT MOVEMENT:")
    print(robot_plan)
    print("OBSTACLE MOVEMENT:")
    print(obs_plan)

if __name__ == "__main__":
    # print(sys.argv)
    start_time = time.time()
    main(sys.argv[1:])
    print("--- %s seconds ---" % (time.time() - start_time))


# add only general motion primitives
# minimize the cost function





