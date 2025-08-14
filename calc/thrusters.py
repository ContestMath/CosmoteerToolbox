# currently only has some basic oc mrt calc

from sympy import *

num_mrt_boosters = symbols("n_mrt")

mrt_base_thrust = 10
mrt_overclock_base_thrsut_bonus = 0.25

oc_mrt_thrust = (mrt_base_thrust + mrt_overclock_base_thrsut_bonus * num_mrt_boosters) * (num_mrt_boosters + 1)
mrt_thrust = mrt_base_thrust * (num_mrt_boosters + 1)

print(oc_mrt_thrust.subs(num_mrt_boosters, 16))
print(mrt_thrust.subs(num_mrt_boosters, 16))
