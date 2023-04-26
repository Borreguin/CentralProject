from pyomo.environ import *

def model1():
    coins = {'penny':1, 'nickel':5, 'dime':10, 'quarter':25, 'half-dollar':50}
    Q = 83

    # writing the model:
    model = ConcreteModel()

    model.x = Var(coins.keys(), domain=NonNegativeIntegers)

    objective = sum(model.x[c] for c in coins.keys())

    constraint1 = sum(model.x[c]*coins[c] for c in coins.keys()) == Q

    constraint2 = model.x['penny'] >= 5

    model.ncoins = Objective(expr = objective, sense=minimize)

    model.cons1 = Constraint(expr =  constraint1)
    model.cons2 = Constraint(expr =  constraint2)

    solver = SolverFactory('glpk')
    solver.solve(model)
    model.pprint()


model1()