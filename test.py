from z3 import *

GRID_SZ = 3
HOPS = 5

OBS_MOVEMENT = [
      (2,2), (2, 3), (1,3), (0, 3), (0, 2), (0, 1)
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
print(s)


########################################################

s.push()
# What is the current time ?
time = 0
obs_pos = OBS_MOVEMENT[time] # (2, 2)

# Don't go anywhere near obs_pos
s.add(And(
Not(X[time][obs_pos[0]][obs_pos[1]]),
Not(X[time][obs_pos[0]][obs_pos[1]]),
Not(X[time][obs_pos[0]][obs_pos[1]]),
Not(X[time][obs_pos[0]][obs_pos[1]]),
Not(X[time][obs_pos[0]][obs_pos[1]])
))


s.add()

# loop {
# }

# Implies(X[t+1][x][y], Or(X[t][x][y] , X[t][x+1][y]
# , X[t][x][y+1]) , X[t][x-1][y] , X[t][r][x][y-1]))
