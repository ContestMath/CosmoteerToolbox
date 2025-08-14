from sympy import *
from sympy.plotting import plot3d
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt
from enum import Enum

beam_count, amp_count, dilation_count, budget = symbols("n, a, d, B")
dilation_count = 0

class DamageTarget(Enum):
    Armor = 1
    ShieldPierce = 2
    ShieldDebuff = 3
damage_target = DamageTarget

def heat_cost(heat_use):
    return heat_use / radiator_dissipation * radiator_cost

def power_cost(power_use):
    return power_use * power_cost_per_1_power

def total_cost_general(base_cost, crew_count, heat_use, power_use):
    crew_cost = crew_count*cost_per_crew
    cost = base_cost + wire_cost + door_cost + crew_cost + power_cost(power_use) + heat_cost(heat_use)
    return cost

def total_cost_pump(base_cost, crew_count, heat_per_beam, power_per_beam):
    base_cost = total_cost_general(base_cost, crew_count, 0, 0)
    pump_heat_cost = heat_cost(heat_per_beam) * beam_count                                  #scales logarithmically with beam count
    pump_power_cost = power_cost(power_per_beam) * beam_count * amp_factor        #scales linearly with beam count
    return base_cost + pump_heat_cost + pump_power_cost

wire_cost = 0.3
radiator_cost = 10
radiator_dissipation = 550
power_cost_per_1_power = 75/10.125      #Assumes useage of non oc LR
door_cost = 0.1
cost_per_crew = 15.6/24                 #Assumes perfect barracks ussage

amp_base_cost = 4.5
amp_heat_per_beam = 100
amp_power_per_beam = 0.2

trl_base_cost = 16
trl_power_use = 0.88
trl_heat_use = 250

trl_utilizationScale = 0.5
trl_efficiency = 0.5
heat_pool_ampo_exponent = 0.67
shield_overload_amp_factor = 0.006
shield_overload_dilation_factor = 0.01
amp_percent = 1.1
dilation_percent = 0.5
amp_factor = 1 / ((beam_count - 1) * trl_utilizationScale + 1)**(1-trl_efficiency)
dilation_factor = amp_factor
thermal_intensity = 1 + amp_factor * amp_percent * amp_count
thermal_radius = 0.5 + dilation_factor * dilation_percent * dilation_count

trl_total_cost = total_cost_general(trl_base_cost, 4, trl_heat_use, trl_power_use)
amp_total_cost = total_cost_pump(amp_base_cost, 0, amp_heat_per_beam, amp_power_per_beam)

budget_equation = Eq(budget, beam_count*trl_total_cost + amp_count*amp_total_cost)
amp_expr = solve(budget_equation, amp_count)[0]

def damage(damage_target):
    if damage_target == DamageTarget.Armor or damage_target == DamageTarget.ShieldPierce:
        return beam_count * thermal_intensity ** heat_pool_ampo_exponent
    #elif damage_target == DamageTarget.ShieldPierce:
        #return beam_count * (thermal_intensity ** heat_pool_ampo_exponent) * (thermal_intensity**0.85 / (250 + thermal_intensity**0.85))
    elif damage_target == DamageTarget.ShieldDebuff:
        return ((thermal_intensity-1) * shield_overload_amp_factor + 1) * ((thermal_radius-0.5) * shield_overload_dilation_factor + 1)

# Creating a system of 2 equations and subbing for amp_count
def subbedDamage(damage_target):
    return simplify(damage(damage_target).subs(amp_count, amp_expr))

def optimal_curve(damage_subbed, budgets, get_gamage = False):
    results = []
    for B in budgets:
        damage_fixed = damage_subbed.subs(budget, B)
        f = lambdify(beam_count, damage_fixed, modules='numpy')
        trl_total_cost_num = float(trl_total_cost) 
        max_beam = max(min(B / trl_total_cost_num, 20),1)
        res = minimize_scalar(lambda b: -f(b), bounds=(1, max_beam), method='bounded')
        if (get_gamage):
            results.append(float(-res.fun))
        else:
            results.append(float(res.x))
        print(res.fun)
    return results

def plot_setup():
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.minorticks_on()
    plt.tick_params(which='major', length=6)
    plt.tick_params(which='minor', length=3)
    plt.show()

def plot_optimal_damage_curve(damage_subbed, max_budgets):
    for max_budget in max_budgets:
        budgets = list(range(40, max_budget, floor(max_budget/100)))
        results = optimal_curve(damage_subbed, budgets, True)
        factor = round(max_budgets[0]/max_budget)
        plt.plot([factor * x for x in budgets], [factor * x for x in results], label=f'num_systems={factor}')

    plt.xlabel('Budget')
    plt.ylabel('Damage')
    plt.title('Optimal Damage vs Budget')
    plot_setup()

def plot_optimal_trl_curve(damage_subbed, max_budgets):
    for max_budget in max_budgets:
        budgets = list(range(40, max_budget, floor(max_budget/100)))
        results = optimal_curve(damage_subbed, budgets)
        plt.plot(budgets, results)

    plt.xlabel('Budget')
    plt.ylabel('#TRL')
    plt.title('Optimal #TRL vs Budget')
    plot_setup()

#plot3d(subbedDamage(damage_target.ShieldDebuff),(budget, 0, 10000),(beam_count, 1, 100),xlabel='Budget', ylabel='Beam Count',zlabel='Damage')
#plot(damage(DamageTarget.ShieldPierce).subs(beam_count, 1)/damage(DamageTarget.ShieldPierce).subs(beam_count, 1).subs(amp_count, 0), (amp_count, 1, 100))
#plot(amp_total.subs(beam_count, 2), (amp_count, 0, 10))
#plot_optimal_damage_curve(subbedDamage(damage_target.Armor), [2001, 1001])
plot_optimal_trl_curve(subbedDamage(damage_target.ShieldPierce), [5001])

