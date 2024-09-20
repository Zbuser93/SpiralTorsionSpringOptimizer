from Calculations import *
import numpy as np
from scipy.optimize import minimize, Bounds

# Bounds:
max_radius_pre = 25
max_aspect_ratio = .75
min_thickness = 2 * nozzle_diameter
max_thickness = height_input * max_aspect_ratio
# min_arclength_E = 96
min_arclength_E_thickness = ( # thickness that results in shortest arclength
        3 * sqrt(2) * sqrt(torque_pre_input / (safety_factor * height_input * yield_stress))
)
if not min_arclength_E_thickness < min_thickness:
    pass
else:
    min_arclength_E_thickness = min_thickness
min_arclength_E = (
        elasticity * height_input * min_arclength_E_thickness**3 * ROM_opt_input
        / (2 * (safety_factor * height_input * yield_stress * min_arclength_E_thickness**2 - 6 * torque_pre_input))
)
max_arclength_E = (
        elasticity * height_input * max_thickness**3 * ROM_opt_input
        / (2 * (safety_factor * height_input * yield_stress * max_thickness**2 - 6 * torque_pre_input))
)
'''max_arclength_E = (
        (pi *
        (max_radius_pre**2 - center_pad_radius**2 + 2 * max_radius_pre * min_thickness + min_thickness**2))
        / min_thickness
)'''

output = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def negative_stiffness(x):
    height = x[0]
    thickness = x[1]
    arclength_E= x[2]
    ROM_opt = x[3]
    torque_pre = x[4]

    stiffness = calculate_stiffness(height, thickness, arclength_E)
    profile_radius = calculate_profile_radius(thickness)
    radius_E = calculate_radius_E(thickness)
    theta_EMD = calculate_theta_EMD(arclength_E, thickness, radius_E)
    radius_pre = calculate_radius_pre(arclength_E, theta_EMD, ROM_opt, radius_E)
    ROM_R = calculate_ROM_R(height, thickness, arclength_E, ROM_opt, torque_pre)
    theta_E = calculate_theta_E(theta_EMD, ROM_R)
    radius_R = calculate_radius_R(arclength_E, theta_E, radius_E)
    pitch_R = calculate_pitch_R(radius_R, radius_E, theta_E)
    profile_revolutions = calculate_profile_revolutions(profile_radius, pitch_R, radius_R)

    output[0] = round(height, 2)
    output[1] = round(thickness, 2)
    output[2] = round(center_pad_radius, 2)
    output[3] = round(pitch_R, 2)
    output[4] = round(profile_radius, 2)
    output[5] = round(profile_revolutions, 2)
    output[6] = round(radius_pre, 2)
    output[7] = round(arclength_E, 2)
    output[8] = round(stiffness, 2)
    output[10] = round(radius_R, 2)
    output[11] = round(ROM_R, 2)

    return -stiffness


def stress_constraint(x):
    """Calculates stress on the string at maximum deformation,
    which ends at minimum coil distance-- not necessarily at
    the point where the spring physically stops. Therefor, if
    a high enough minimum coil distance is set, the spring
    could still be damaged by deforming it past that point."""
    height = x[0]
    thickness = x[1]
    arclength_E = x[2]
    ROM_opt = x[3]
    torque_pre = x[4]
    ROM_R = calculate_ROM_R(height, thickness, arclength_E, ROM_opt, torque_pre)
    stress_max = (elasticity * thickness * ROM_R) / (2 * arclength_E)
    output[9] = stress_max - safety_factor * yield_stress
    return -output[9] # >= 0


def positive_radius_constraint(x): # radius_R > radius_E
    height = x[0]
    thickness = x[1]
    arclength_E = x[2]
    ROM_opt = x[3]
    torque_pre = x[4]
    radius_E = calculate_radius_E(thickness)
    ROM_R = calculate_ROM_R(height, thickness, arclength_E, ROM_opt, torque_pre)
    theta_EMD = calculate_theta_EMD(arclength_E, thickness, radius_E)
    theta_E = calculate_theta_E(theta_EMD, ROM_R)
    radius_R = calculate_radius_R(arclength_E, theta_E, radius_E)
    return radius_R - radius_E # >= 0


def max_radius_constraint(x):
    thickness = x[1]
    arclength_E = x[2]
    ROM_opt = x[3]
    radius_E = calculate_radius_E(thickness)
    theta_EMD = calculate_theta_EMD(arclength_E, thickness, radius_E)
    radius_pre = calculate_radius_pre(arclength_E, theta_EMD, ROM_opt, radius_E)
    return max_radius_pre - radius_pre # == 0


def aspect_ratio_constraint(x):
    height = x[0]
    thickness = x[1]
    return max_aspect_ratio - thickness / height # >= 0


def optimize_spring():
    initial_guess = np.array(
        [height_input, min_arclength_E_thickness, min_arclength_E, ROM_opt_input, torque_pre_input]
    )
    bounds = Bounds(
        [height_input, min_thickness, min_arclength_E, ROM_opt_input, torque_pre_input],
        [height_input, max_thickness, max_arclength_E, ROM_opt_input, torque_pre_input]
    )
    constraints = [
        {'type': 'ineq', 'fun': stress_constraint},
        {'type': 'ineq', 'fun': positive_radius_constraint},
        {'type': 'eq', 'fun': max_radius_constraint},
        {'type': 'ineq', 'fun': aspect_ratio_constraint}
    ]
    solution = minimize(
        fun=negative_stiffness,
        x0=initial_guess,
        bounds=bounds,
        constraints=constraints
    )
    print('Status : %s' % solution['message'])
    print('Total Evaluations: %d' % solution['nfev'])
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
