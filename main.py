from config import init     # create project structure

# test if cplex environment exists
from docplex.mp.environment import Environment
env = Environment()
print(env.print_information())


