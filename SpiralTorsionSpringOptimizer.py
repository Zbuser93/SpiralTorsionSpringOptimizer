from Calculations import *
from scipy.optimize import shgo, Bounds

# Bounds:
max_radius_pre = 25
max_aspect_ratio = 1
min_thickness = 2 * nozzle_diameter
max_thickness = height_input * max_aspect_ratio
# min_arclength_E = 96
min_arclength_E_thickness = ( # thickness that results in the shortest possible arclength
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
        pi * (max_radius_pre - center_pad_radius / (2 * min_thickness)) * (max_radius_pre + center_pad_radius)
)
'''max_arclength_E = (
        elasticity * height_input * max_thickness**3 * ROM_opt_input
        / (2 * (safety_factor * height_input * yield_stress * max_thickness**2 - 6 * torque_pre_input))
)
max_arclength_E = (
        (pi *
        (max_radius_pre**2 - center_pad_radius**2 + 2 * max_radius_pre * min_thickness + min_thickness**2))
        / min_thickness
)'''

output = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def negative_stiffness(x):
    thickness = x[0]
    arclength_E= x[1]

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

    output[0] = round(height_input, 2)
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
    thickness = x[0]
    arclength_E = x[1]
    ROM_R = calculate_ROM_R(height_input, thickness, arclength_E, ROM_opt_input, torque_pre_input)
    stress_max = (elasticity * thickness * ROM_R) / (2 * arclength_E)
    output[9] = stress_max - safety_factor * yield_stress
    return -output[9] # >= 0


def positive_radius_constraint(x): # radius_R > radius_E
    thickness = x[0]
    arclength_E = x[1]
    radius_E = calculate_radius_E(thickness)
    ROM_R = calculate_ROM_R(height_input, thickness, arclength_E, ROM_opt_input, torque_pre_input)
    theta_EMD = calculate_theta_EMD(arclength_E, thickness, radius_E)
    theta_E = calculate_theta_E(theta_EMD, ROM_R)
    radius_R = calculate_radius_R(arclength_E, theta_E, radius_E)
    return radius_R - radius_E # >= 0


def max_radius_constraint(x):
    thickness = x[0]
    arclength_E = x[1]
    radius_E = calculate_radius_E(thickness)
    theta_EMD = calculate_theta_EMD(arclength_E, thickness, radius_E)
    radius_pre = calculate_radius_pre(arclength_E, theta_EMD, ROM_opt_input, radius_E)
    return max_radius_pre - radius_pre # == 0


def optimize_spring():
    bounds = Bounds(
        [min_thickness, min_arclength_E],
        [max_thickness, max_arclength_E]
    )
    constraints = [
        {'type': 'ineq', 'fun': stress_constraint},
        {'type': 'ineq', 'fun': positive_radius_constraint},
        {'type': 'eq', 'fun': max_radius_constraint}
    ]
    solution = shgo(
        func=negative_stiffness,
        bounds=bounds,
        constraints=constraints,
        n=50000
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
    print(f'{min_arclength_E}')
    print(max_arclength_E)
