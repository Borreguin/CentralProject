import pyomo.environ as pm


def run_model(df_segment, aircrafts, cost, position, time, disp):
    model = pm.ConcreteModel()
    days = df_segment.index
    max_time = max(df_segment['end'])

    # x is the initial position
    # e = wished departure
    # f = wished arrive
    # y is the final position

    # Sets:
    model.A = pm.Set(initialize=aircrafts)
    model.D = pm.Set(initialize=days)

    # selection variable
    model.b = pm.Var(model.A, model.D, domain=pm.Boolean, initialize=False)
    only_one = sum(model.b[a, d] for a in aircrafts for d in days) == 1

    model.tx = pm.Var(model.A, model.D, domain=pm.NonNegativeReals, bounds=(0, max_time), initialize=0)
    # model.te = Var(aircrafts, domain=NonNegativeReals, bounds=(0, tv_f))
    # model.tf = Var(aircrafts, domain=NonNegativeReals, bounds=(0, tv_f))
    model.ty = pm.Var(model.A, model.D, domain=pm.NonNegativeReals, bounds=(0, max_time), initialize=0)

    objective = sum(model.b[a, d] * (
            cost[a][f][position[a]['p_fin'][d]] + cost[a][e][f] + cost[a][f][position[a]['p_fin'][d]]
    ) for a in aircrafts for d in days)

    model.cost = pm.Objective(expr=objective, sense=pm.minimize)
    model.only_one = pm.Constraint(expr=only_one)

    def timeConstraint(model, a, d):
        pos_ini = position[a]['p_ini'][d]
        pos_fin = position[a]['p_fin'][d]
        return model.ty[a, d] - model.tx[a, d] == (
                time[a][pos_ini][e] + time[a][e][f] + time[a][f][pos_fin]
        ) * model.b[a, d]

    model.TimeConstraint = Constraint(model.A, model.D, rule=timeConstraint)

    def available_constraint_tx(model, a, d):
        return model.tx[a, d] >= disp[a]['tv_i'][d] * model.b[a, d]

    model.AvailableConstraintTX = pm.Constraint(model.A, model.D, rule=available_constraint_tx)

    def available_constraint_ty(model, a, d):
        return model.ty[a, d] <= disp[a]['tv_f'][d] * model.b[a, d]

    model.AvailableConstraintTY =pm.Constraint(model.A, model.D, rule=available_constraint_ty)

    solver = pm.SolverFactory('glpk')
    results = solver.solve(model)
    # model.pprint()
    return results
