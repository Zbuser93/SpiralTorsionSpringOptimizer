from Calculations import *
from pyswarm import pso

# Bounds:
max_radius_pre = 25
max_aspect_ratio = .75
min_thickness = 2 * nozzle_diameter
max_thickness = height_input * max_aspect_ratio
min_arclength_E_thickness = ( # thickness that results in shortest arclength
        3 * sqrt(2) * sqrt(torque_pre_input / (safety_factor * height_input * yield_stress))
)
if min_arclength_E_thickness < min_thickness:
    min_arclength_E_thickness = min_thickness
min_arclength_E = (
        elasticity * height_input * min_arclength_E_thickness**3 * ROM_opt_input
        / (2 * (safety_factor * height_input * yield_stress * min_arclength_E_thickness**2 - 6 * torque_pre_input))
)
max_arclength_E = (
        pi * (max_radius_pre - center_pad_radius / (2 * min_thickness)) * (max_radius_pre + center_pad_radius)
)


output = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def negative_stiffness(x):
    thickness = x[0]
    arclength_E = x[1]

    stiffness = calculate_stiffness(height_input, thickness, arclength_E)
    profile_radius = calculate_profile_radius(thickness)
    radius_E = calculate_radius_E(thickness)
    theta_EMD = calculate_theta_EMD(arclength_E, thickness, radius_E)
    radius_pre = calculate_radius_pre(arclength_E, theta_EMD, ROM_opt_input, radius_E)
    ROM_R = calculate_ROM_R(height_input, thickness, arclength_E, ROM_opt_input, torque_pre_input)
    theta_E = calculate_theta_E(theta_EMD, ROM_R)
    radius_R = calculate_radius_R(arclength_E, theta_E, radius_E)
    pitch_R = calculate_pitch_R(radius_R, radius_E, theta_E)
    profile_revolutions = calculate_profile_revolutions(profile_radius, pitch_R, radius_R)

    output[0] = height_input
    output[1] = thickness
    output[2] = center_pad_radius
    output[3] = pitch_R
    output[4] = profile_radius
    output[5] = profile_revolutions
    output[6] = radius_pre
    output[7] = arclength_E
    output[8] = stiffness
    output[10] = radius_R
    output[11] = ROM_R

    return -stiffness


def stress_constraint(thickness, arclength_E):
    """Calculates stress on the string at maximum deformation,
    which ends at minimum coil distance-- not necessarily at
    the point where the spring physically stops. Therefor, if
    a high enough minimum coil distance is set, the spring
    could still be damaged by deforming it past that point."""
    ROM_R = calculate_ROM_R(height_input, thickness, arclength_E, ROM_opt_input, torque_pre_input)
    stress_max = (elasticity * thickness * ROM_R) / (2 * arclength_E)
    output[9] = stress_max - safety_factor * yield_stress
    return -output[9] # >= 0


def positive_radius_constraint(thickness, arclength_E): # radius_R > radius_E
    radius_E = calculate_radius_E(thickness)
    ROM_R = calculate_ROM_R(height_input, thickness, arclength_E, ROM_opt_input, torque_pre_input)
    theta_EMD = calculate_theta_EMD(arclength_E, thickness, radius_E)
    theta_E = calculate_theta_E(theta_EMD, ROM_R)
    radius_R = calculate_radius_R(arclength_E, theta_E, radius_E)
    return radius_R - radius_E # >= 0


def max_radius_constraint(thickness, arclength_E):
    radius_E = calculate_radius_E(thickness)
    theta_EMD = calculate_theta_EMD(arclength_E, thickness, radius_E)
    radius_pre = calculate_radius_pre(arclength_E, theta_EMD, ROM_opt_input, radius_E)
    return max_radius_pre - radius_pre # == 0


def constraints(x):
    thickness = x[0]
    arclength_E = x[1]
    c1 = stress_constraint(thickness, arclength_E)
    c2 = positive_radius_constraint(thickness, arclength_E)
    c3 = max_radius_constraint(thickness, arclength_E)
    return [c1, c2, c3]


def optimize_spring():
    lb = [min_thickness, min_arclength_E]
    ub = [max_thickness, max_arclength_E]
    xopt, fopt = pso(negative_stiffness, lb, ub, f_ieqcons=constraints)
    print(xopt)
    print(fopt)
    print()
    print(f'height: {output[0]}mm')
    print(f'thickness: {output[1]}mm')
    print(f'center pad radius: {output[2]}mm')
    print(f'pitch @ rest: {output[3]}')
    print(f'profile radius: {output[4]}mm')
    print(f'profile revolutions: {output[5]}')
    print(f'radius @ preload deformation: {output[6]}mm')
    print(f'radius @ rest: {output[10]}mm')
    print(f'range of motion from rest: {output[11]}')
    print(f'spring arclength: {output[7]}mm')
    print(f'spring stiffness: {output[8]}Nmm/RAD')
    print(f'stress constraint: {round(output[9], 2)}')


if __name__ == '__main__':
    print()
    optimize_spring()
    print()
    print('arclength range:')
    print(f'{min_arclength_E} @ {min_arclength_E_thickness}')
    print(max_arclength_E)
