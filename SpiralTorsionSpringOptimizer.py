import numpy as np
from pyswarm import pso

class SpiralTorsionSpring:
    def __init__(self, height, thickness, radius_center, pitch_0, pitch_R, number_revolutions):
        self.height = height
        self.thickness = thickness
        self.radius_center = radius_center
        self.pitch_0 = pitch_0
        self.pitch_R = pitch_R
        self.number_revolutions = number_revolutions

    def __repr__(self):
        return[
            print(f'height: {self.height}mm'),
            print(f'thickness: {self.thickness}mm'),
            print(f'center pad radius: {self.radius_center}mm'),
            print(f'minimum coil distance: {self.pitch_0}mm'),
            print(f'pitch @ rest: {self.pitch_R}'),
            print(f'revolutions at rest: {self.number_revolutions}')
        ]

    @classmethod
    def maximize_stiffness(
            cls, height, elasticity, max_radius_pre, radius_center, pitch_0, deltatheta_opt,
            torque_pre, safety_factor, stress_yield, max_thickness=None, nozzle_diameter=0.0):

        #calculate bounds:
        min_thickness = 2 * nozzle_diameter
        if max_thickness is None:
            max_thickness = max_radius_pre
        min_arclength_E_thickness = (  # thickness that results in shortest arclength
                3 * np.sqrt(2) * np.sqrt(torque_pre / (safety_factor * height * stress_yield))
        )
        if min_arclength_E_thickness < min_thickness:
            min_arclength_E_thickness = min_thickness
        min_arclength_E = (
                elasticity * height * min_arclength_E_thickness ** 3 * deltatheta_opt
                / (2 * (safety_factor * height * stress_yield * min_arclength_E_thickness ** 2 - 6 * torque_pre))
        )
        max_arclength_E = (
                np.pi * (max_radius_pre - radius_center / (2 * min_thickness)) * (max_radius_pre + radius_center)
        )
        lb = [min_thickness, min_arclength_E]
        ub = [max_thickness, max_arclength_E]

        #set up args:
        args = (height, elasticity, max_radius_pre, radius_center,
                pitch_0, deltatheta_opt, torque_pre, safety_factor, stress_yield)

        #optimize spring:
        xopt, fopt = pso(cls.negative_stiffness, lb, ub, f_ieqcons=cls.cons_ms, args=args)

        #calculate remaining properties:
        thickness = xopt[0]
        arclength_E = xopt[1]
        radius_E = cls.calculate_radius_E(thickness, radius_center, pitch_0)
        deltatheta_R = cls.calculate_deltatheta_R(height, elasticity, thickness, arclength_E, deltatheta_opt, torque_pre)
        theta_EMD = cls.calculate_theta_EMD(arclength_E, thickness, radius_E, pitch_0)
        theta_E = cls.calculate_theta_E(theta_EMD, deltatheta_R)
        radius_R = cls.calculate_radius_R(arclength_E, theta_E, radius_E)
        pitch_R = cls.calculate_pitch_R(radius_R, radius_E, theta_E)
        number_revolutions = cls.calculate_number_revolutions(theta_E)

        #create instance:
        return cls(height, thickness, radius_center, pitch_0, pitch_R, number_revolutions)

    '''the next two functions are not static, but must be treated as such due to a bug in pyswarm'''
    @staticmethod
    def cons_ms(x, *args):
        thickness = x[0]
        arclength_E= x[1]
        height = args[0]
        elasticity = args[1]
        max_radius_pre = args[2]
        radius_center = args[3]
        pitch_0 = args[4]
        deltatheta_opt = args[5]
        torque_pre = args[6]
        safety_factor = args[7]
        stress_yield = args[8]
        radius_E = SpiralTorsionSpring.calculate_radius_E(thickness, radius_center, pitch_0)
        deltatheta_R = SpiralTorsionSpring.calculate_deltatheta_R(height, elasticity, thickness, arclength_E, deltatheta_opt, torque_pre)
        theta_EMD = SpiralTorsionSpring.calculate_theta_EMD(arclength_E, thickness, radius_E, pitch_0)
        stress_max = SpiralTorsionSpring.calculate_stress_max(thickness, deltatheta_R, arclength_E, elasticity)
        radius_pre = SpiralTorsionSpring.calculate_radius_pre(arclength_E, theta_EMD, deltatheta_opt, radius_E)
        #stress constraint:
        c1 = -(stress_max - safety_factor * stress_yield)
        #positive radius constraint:
        c2 = radius_pre - radius_E
        #max radius constraint:
        c3 = max_radius_pre - radius_pre
        return [c1, c2, c3]

    @staticmethod
    def negative_stiffness(x, *args):
        thickness = x[0]
        arclength_E = x[1]
        height = args[0]
        elasticity = args[1]
        stiffness = SpiralTorsionSpring.calculate_stiffness(height, elasticity, thickness, arclength_E)
        return -stiffness

    @staticmethod
    def calculate_stiffness(
            height, elasticity, thickness, arclength_E):
        return (elasticity * height * thickness ** 3) / (12 * arclength_E)

    @staticmethod
    def calculate_arclength_E(
            height, elasticity, thickness, stiffness):
        return (elasticity * height * thickness ** 3) / (12 * stiffness)

    @staticmethod
    def calculate_radius_E(
            thickness, radius_center, pitch_0):
        return radius_center + thickness / 2 + pitch_0

    @staticmethod
    def calculate_theta_EMD(
            arclength_E, thickness, radius_E, pitch_0):
        theta_IMD = (2 * np.pi * radius_E) / (thickness + pitch_0)
        arclength_IMD = np.pi * radius_E * (theta_IMD / (2 * np.pi))
        arclength_MD = arclength_E + arclength_IMD
        theta_MD = np.sqrt((4 * np.pi * arclength_MD) / (thickness + pitch_0))
        return theta_MD - theta_IMD

    @staticmethod
    def calculate_radius_pre(
            arclength_E, theta_EMD, deltatheta_opt, radius_E):
        theta_pre = theta_EMD - deltatheta_opt
        return (2 * arclength_E) / theta_pre - radius_E

    @staticmethod
    def calculate_deltatheta_R(
            height, elasticity, thickness, arclength_E, deltatheta_opt, torque_pre):
        deltatheta_pre = (2 * arclength_E * 6 * torque_pre) / (elasticity * height * thickness ** 3)
        return deltatheta_pre + deltatheta_opt

    @staticmethod
    def calculate_theta_E(
            theta_EMD, deltatheta_R):
        return theta_EMD - deltatheta_R

    @staticmethod
    def calculate_radius_R(
            arclength_E, theta_E, radius_E):
        return (2 * arclength_E) / theta_E - radius_E

    @staticmethod
    def calculate_pitch_R(
            radius_R, radius_E, theta_E):
        return (2 * np.pi * (radius_R - radius_E)) / theta_E

    @staticmethod
    def calculate_number_revolutions(
            theta_E):
        return theta_E / (2 * np.pi)

    @staticmethod
    def calculate_stress_max(
            thickness, deltatheta_R, arclength_E, elasticity):
        return (elasticity * thickness * deltatheta_R) / (2 * arclength_E)

    @staticmethod
    def calculate_torque_max(
            stress_max, height, thickness):
        return (stress_max * height * thickness ** 2) / 6

if __name__ == '__main__':
    input_height = 4
    input_elasticity = 3100
    input_max_radius_pre = 25
    input_radius_center = 8
    input_pitch_0 = 0.5
    input_deltatheta_opt = 3
    input_torque_pre = 10
    input_safety_factor = .75
    input_stress_yield = 83
    input_max_thickness = 4
    input_nozzle_diameter = 0.4
    spring1 = SpiralTorsionSpring.maximize_stiffness(
        input_height, input_elasticity, input_max_radius_pre, input_radius_center, input_pitch_0,
        input_deltatheta_opt, input_torque_pre, input_safety_factor, input_stress_yield,
        max_thickness=input_max_thickness, nozzle_diameter=input_nozzle_diameter
    )
    spring1.__repr__()
