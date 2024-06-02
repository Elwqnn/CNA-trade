#!/usr/bin/env python3

##
## EPITECH PROJECT, 2024
## CNA-trade
## File description:
## set_generator
##

import os
from math import cos, sin, sqrt
from random import gauss, randint
from numpy import linspace
from matplotlib import pyplot as plt

# Parameters - modify as needed
noise = 2
cycle = 15
frequency = 30
size = 720
tlen = 80
tmax = 20

def generate_trend():
    trend = []
    sign = 1
    while len(trend) <= size:
        trend += list(linspace(tmax * (4 + sign), tmax * (4 - sign), tlen + randint(0, int(tlen / 2))))
        sign = -sign
    return trend[:size + 1]

trend1 = generate_trend()
trend2 = generate_trend()

def generate_data(trend):
    return [sin(frequency * i / size) * cycle + gauss(0, 1) * noise + trend[i] for i in range(size)]

gen1 = [0] + generate_data(trend1)
gen2 = [0] + generate_data(trend2)

input_file = "datasets/template-set.csv"
output_file = "datasets/new-set.csv"

with open(input_file, "r") as f, open(output_file, "w") as g:
    lines_written = 0
    for line in f:
        if len(line) < 2 or line.startswith("p"):
            g.write(line)
            lines_written += 1
        else:
            data = line.split(",")
            i = lines_written + 1
            if i in range(1, size + 1):
                nvals = [gen1[i], gen1[i] * 0.95, gen1[i] * (1 - gauss(0.025, 0.005)), gen1[i] * (1 - gauss(0.025, 0.005))]
            elif i in range(size + 1, 2 * size + 1):
                nvals = [gen2[i - size], gen2[i - size] * 0.95, gen2[i - size] * (1 - gauss(0.025, 0.005)), gen2[i - size] * (1 - gauss(0.025, 0.005))]
            elif i > 2 * size:
                nvals = [
                    gen2[i - 2 * size] / gen1[i - 2 * size],
                    gen2[i - 2 * size] / gen1[i - 2 * size],
                    gen2[i - 2 * size] / gen1[i - 2 * size] * (1 - gauss(0.025, 0.005)),
                    gen2[i - 2 * size] / gen1[i - 2 * size] * (1 - gauss(0.025, 0.005))
                ]
            g.write(data[0] + "," + data[1] + ",")
            g.write(",".join(map(str, nvals)))
            g.write("," + data[6])
            lines_written += 1

x = linspace(1, size, size)
plt.plot(x, gen1[1:], label="Generation 1")
plt.plot(x, gen2[1:], label="Generation 2")
plt.legend()
plt.show()
