from z3 import *

def intersection_points(robot_pos, obs_pos):
    (rx, ry) = robot_pos
    (obx, oby) = obs_pos # (a, b)

    robot_halo = set([(rx, ry), (rx+1, ry), (rx, ry+1), (rx, ry-1), (rx-1,ry)])
    obs_halo = set([(obx, oby),(obx+1, oby), (obx, oby+1), (obx-1, oby),(obx, oby-1)])
    return list(robot_halo.intersection(obs_halo))

def print_plan(m):
    return sorted([d.name() for d in m.decls() if m[d]==True])

def get_robot_pos(m,time):
    (_, _, x, y) = sorted([d.name() for d in m.decls() if m[d]==True])[time].split('_')
    return (int(x), int(y)) 
    
GRID_SZ = 4
HOPS = 10

OBS_MOVEMENT = [
      (2,2), (2, 3), (1,3), (0, 3), (0, 2), (0, 1), (0, 1)
      , (0, 1)
      , (0, 1)
      , (0, 1)
      , (0, 1)
      , (0, 1)
      , (0, 1)
      , (0, 1)
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

# Motion primitives

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
            #     print(simplify(Implies(X[t+1][x][y], temp)))
                s.add(simplify(Implies(X[t+1][x][y], temp)))
# print(s)


########################################################
# What is the current time ?
time = 0
obs_pos = OBS_MOVEMENT[time] # (2, 2)
robot_pos = (0, 0) # (0, 0)

s.push()
for (x, y) in intersection_points(robot_pos, obs_pos):
    s.add(Not(X[time][x][y]))

while (time < HOPS):
    if s.check() == unsat:
        print("Stay there")
        time += 1
        continue

    m = s.model()
    s.pop()
    
    obs_pos = OBS_MOVEMENT[time] # (2, 2)
    robot_pos = get_robot_pos(m, time) # (0, 0)
    print("robot at ",robot_pos, "at ", time)
    print("obs at ",obs_pos, "at ", time)

    s.push()

    print(intersection_points(robot_pos, obs_pos))
    for (x, y) in intersection_points(robot_pos, obs_pos):
        s.add(Not(X[time][x][y]))
    time += 1