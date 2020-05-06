from z3 import *

def intersection_points(robot_pos, obs_pos):
    (rx, ry) = robot_pos
    (obx, oby) = obs_pos # (a, b)

    robot_halo = set([(rx, ry), (rx+1, ry), (rx, ry+1), (rx, ry-1), (rx-1,ry)])
    obs_halo = set([(obx, oby),(obx+1, oby), (obx, oby+1), (obx-1, oby),(obx, oby-1)])
    return list(robot_halo.intersection(obs_halo))

def get_plan(m):
    
    # sorted([i.split('_') for i in l], key=lambda item: int(item[1]))
    return sorted([d.name() for d in m.decls() if m[d]==True], key=lambda item: int(item.split('_')[1]))

def get_robot_pos(m,time):
    (_, _, x, y) = get_plan(m)[time].split('_') 
    return (int(x), int(y)) 
    
GRID_SZ = 4
HOPS = 10

OBS_MOVEMENT = [
      (0, 3)
      , (0, 3)
      , (0, 3)
      , (0, 3)
      , (0, 2)
      , (0, 2)
      , (0, 3)
      , (0, 3)
      , (0, 3)
      , (0, 3)
      , (0, 3)
]

# X is a three dimensional grid containing (t, x, y)
X =  [ [ [ Bool("x_%s_%s_%s" % (k, i, j)) for j in range(GRID_SZ) ]
      for i in range(GRID_SZ) ] 
      for k in range(HOPS+1)]

s = Solver()

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


########################################################

time = 0
s.check()


# m = s.model()


while (time < HOPS):
    
    robot_pos = (0, 0) if time == 0 else get_robot_pos(m,time)
    obs_pos = OBS_MOVEMENT[time]
    s.add(X[time][robot_pos[0]][robot_pos[1]])
    print("time is ", time)
    print("robot at ", robot_pos)
    print("obs at ", obs_pos)
    
    s.push()
    print("intersection points")
    print(intersection_points(robot_pos, obs_pos))
    
    for (x, y) in intersection_points(robot_pos, obs_pos):
        s.add(Not(X[time+1][x][y]))
    
    if s.check() == unsat:
        print("stay there")
    else:
        m = s.model()
        print("Plan for time = " + str(time+1))
        print(get_plan(m))
        
    s.pop()
    time += 1

robot_pos = get_robot_pos(m,time)
obs_pos = OBS_MOVEMENT[time]
print("time is ", time)
print("robot at ", robot_pos)
print("obs at ", obs_pos)