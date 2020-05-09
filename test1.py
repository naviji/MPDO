from z3 import *

GRID_SZ = 4
HOPS = 10


###############################################################
#get an integer  for the state
def state(time , x , y):

    return Bool(str(GRID_SZ * ( HOPS * (time) + x ) + y + 1))


##################################################################
#get the state variable values
def variables(state):
    state = int(str(state))
    print(state)
    state -= 1
    y = state % GRID_SZ
    
    state //= GRID_SZ
    x = state % GRID_SZ

    state //= GRID_SZ
    time = state % HOPS

    return time, x, y


###########################################################

print(variables(state(4,4,4)))

#Solver object
s = Solver()

# Initial constraints
s.add(state(0,0,0))
for x in range(GRID_SZ):
    for y in range(GRID_SZ):
        if x == 0 and y == 0:
            continue
        else:
            s.add(Not(state(0,x,y)))


#Final constraints
s.add(state(HOPS,GRID_SZ-1,GRID_SZ-1))
for x in range(GRID_SZ-1):
    for y in range(GRID_SZ-1):
        s.add(Not(state(HOPS,x,y)))


#Motion premitive
for time in range(HOPS):
    for x in range(GRID_SZ):
        for y in range(GRID_SZ):
            temp = Or(state(time, x, y))
            if x-1 >= 0:
                temp = Or(temp, state(time, x-1, y))
            if y-1 >= 0:
                temp = Or(temp, state(time, x, y-1))
            if x+1 < GRID_SZ:
                temp = Or(temp, state(time, x+1, y))
            if y+1 < GRID_SZ:
                temp = Or(temp, state(time, x, y+1))
            s.add(simplify(Implies(state(time+1, x, y), temp)))
            
