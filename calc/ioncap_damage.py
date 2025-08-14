# This is pretty incomplete and broken

from math import *

switch_time = 0.1

class Capacitor:
    def __init__(self, ion_count, charge_time):
        self.ion_count = ion_count
        self.filltime = ion_count/10
        self.charge_time = charge_time

    def damage(self, input_damage):
        total = 0
        for i in range(floor(self.charge_time/self.filltime)):
            total += input_damage*0.75**i
        return total


class MultiCapacitor:
    def __init__(self, caps):
        self.caps = caps
        self.outputtime = caps[-1].filltime
    
    def damage(self, input_damage):
        total = input_damage
        for cap in self.caps:
            total = cap.damage(total)
        return total
    
    def charge_time(self):
        total = 1
        for cap in self.caps:
            total = total*cap.charge_time+switch_time
        return total
 
def partitions(z, n, min_val=1):
    if n == 0:
        return [[]] if n == 0 else []
    if n == 1:
        if z >= min_val:
            return [[z]]
        return []
    return [[i] + rest for i in range(min_val, z - n + 2)
                     for rest in partitions(z - i, n - 1, i)]

prism_amount = 10
charge_time = 60
pairs = [[i, j] for i in range(0, prism_amount + 1) for j in range(0, charge_time + 1)]
cap_max_amount = 2

for cap_amount in range(cap_max_amount+1):
    caps = []
    prism_partitions = partitions(prism_amount, cap_amount)
    charge_time_partition_percentages = partitions(10, cap_amount)     #Partitioned in steps of 10%
    charge_time_partition_percentages = [[x/10 for x in sublist] for sublist in charge_time_partition_percentages]

    for prism_partition in prism_partitions:
        charge_time_partitions = []
        for partitiom in charge_time_partition_percentages:
            new_partition = []
            l = len(partitiom)
            f = 1
            for i in range(len(partitiom)):
                new_element = (charge_time*prism_amount)**(1-i)*partitiom[i]*prism_partition[i]
                if i != 0:
                    new_element /= partitiom[i-1]*prism_partition[i-1]
                new_partition = [new_element] + new_partition
            charge_time_partitions.append(new_partition)
            print(charge_time_partitions)
        for charge_time_partition in charge_time_partitions:
            caps = []
            for i in range(len(prism_partition)):
                caps.append(Capacitor(prism_partition[i], charge_time_partition[i]))
            if not caps:
                continue
            cap = MultiCapacitor(caps)
            #print(prism_partition)
            #print(charge_time_partition)
            #print(cap.damage(1))
            #print(cap.charge_time())
