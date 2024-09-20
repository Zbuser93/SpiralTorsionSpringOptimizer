from math import pi, sqrt

# Settings:
nozzle_diameter = 0.4
elasticity = 3100
yield_stress = 83
safety_factor = 0.75
min_coil_distance = 0.25
center_pad_radius = 10

# Inputs:
ROM_opt_input = 6.28
torque_pre_input = 0.1
height_input = 4
thickness_input = 3
stiffness_input = 323.53


def calculate_stiffness(
        height, thickness, arclength_E):
    return (elasticity * height * thickness ** 3) / (12 * arclength_E)


def calculate_arclength_E(
        height, thickness, stiffness):
    return (elasticity * height * thickness ** 3) / (12 * stiffness)


def calculate_profile_radius(
        thickness):
    return center_pad_radius - thickness / 2


def calculate_radius_E(
        thickness):
    return center_pad_radius + thickness / 2


def calculate_theta_EMD(
        arclength_E, thickness, radius_E):
    theta_IMD = (2 * pi * radius_E) / (thickness + min_coil_distance)
    arclength_IMD = pi * radius_E * (theta_IMD / (2 * pi))
    arclength_MD = arclength_E + arclength_IMD
    theta_MD = sqrt((4 * pi * arclength_MD) / (thickness + min_coil_distance))
    return theta_MD - theta_IMD


def calculate_radius_pre(
        arclength_E, theta_EMD, ROM_opt, radius_E):
    theta_E_pre = theta_EMD - ROM_opt
    return (2 * arclength_E) / theta_E_pre - radius_E


def calculate_ROM_R(
        height, thickness, arclength_E, ROM_opt, torque_pre):
    ROM_pre = (2 * arclength_E * 6 * torque_pre) / (elasticity * height * thickness ** 3)
    return ROM_pre + ROM_opt


def calculate_theta_E(
        theta_EMD, ROM_R):
    return theta_EMD - ROM_R


def calculate_radius_R(
        arclength_E, theta_E, radius_E):
    return (2 * arclength_E) / theta_E - radius_E


def calculate_pitch_R(
        radius_R, radius_E, theta_E):
    return (2 * pi * (radius_R - radius_E)) / theta_E


def calculate_profile_revolutions(
        profile_radius, pitch_R, radius_R):
    theta_OP = (2 * pi * profile_radius) / pitch_R
    theta_R = (2 * pi * radius_R) / pitch_R
    theta_P = theta_R - theta_OP
    return theta_P / (2 * pi)


def calculate_torque_max(
        thickness, ROM_R, arclength_E, height):
    stress_max = (elasticity * thickness * ROM_R) / (2 * arclength_E)
    return (stress_max * height * thickness ** 2) / 6
