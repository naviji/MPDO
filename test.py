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
    (_, _, x, y) = sorted([d.name() for d in m.decls() if m[d]==True], key=lambda item: int(item.split('_')[1]))[time].split('_')
    return (int(x), int(y)) 
    
GRID_SZ = 4
HOPS = 10

OBS_MOVEMENT = [
      (0, 3)
      , (0, 3)
      , (0, 3)
      , (0, 3)
      , (0, 3)
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
# for grid in X:
#     for i in range(len(grid)):
#         for j in range(len(grid)):
#             for p in range(len(grid)):
#                 for q in range(len(grid)):
#                     if not (i==p and j==q):
#                         s.add(And(grid[i][j], Not(grid[p][q])))

# Safety constraints
# s.add(X[HOPS][GRID_SZ-1][GRID_SZ-1])
# s.add([Not(cell) for row in X[HOPS] for cell in row][:-1])



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
            #     print(simplify(Implies(X[t+1][x][y], temp)))
                s.add(simplify(Implies(X[t+1][x][y], temp)))
# print(s)


########################################################
time = 0
obs_pos = OBS_MOVEMENT[time] # (2, 2)
robot_pos = (0, 0) # (0, 0)

time += 1
s.push()
for (x, y) in intersection_points(robot_pos, obs_pos):
    s.add(Not(X[time][x][y]))

# obs_pos = OBS_MOVEMENT[time] # (2, 2)
# robot_pos = get_robot_pos(m, time) # (0, 0)

for a in s.assertions():
    print(a)
# print(s)
# 0 -> 9


# THE PROBLEM WITH SCOPE!
while (time < HOPS):
    print("TIME IS %s" % time)
    print("robot at ",robot_pos, "at ", time)
    print("obs at ",obs_pos, "at ", time)

    if s.check() == unsat:
        print("Stay there")
        time += 1
        continue

    m = s.model()

    s.pop()
    s.push()
    time += 1
    print(intersection_points(robot_pos, obs_pos))
    for (x, y) in intersection_points(robot_pos, obs_pos):
        s.add(Not(X[time][x][y]))
        print(Not(X[time][x][y]))
    
        
    # for a in s.assertions():
    #     print(a)

    obs_pos = OBS_MOVEMENT[time] # (2, 2)
    robot_pos = get_robot_pos(m, time) # (0, 0)
m = s.model()
# time is 10
print("robot at ",robot_pos, "at ", time)
print("obs at ",obs_pos, "at ", time)
# print(get_plan(m))