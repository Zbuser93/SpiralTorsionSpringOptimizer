import numpy as np
from pyswarm import pso

class SpiralTorsionSpring:
    def __init__(
            self, height, thickness, radius_center, pitch_0, pitch_R, number_revolutions,
            arclength_E, elasticity, radius_pre, deltatheta_opt, torque_pre, safety_factor,
            stress_yield, stiffness, unutilized_elasticity, torque_pre_max
    ):
        self.height = height
        self.thickness = thickness
        self.radius_center = radius_center
        self.pitch_0 = pitch_0
        self.pitch_R = pitch_R
        self.number_revolutions = number_revolutions
        self.arclength_E = arclength_E
        self.elasticity = elasticity
        self.radius_pre = radius_pre
        self.deltatheta_opt = deltatheta_opt
        self.torque_pre = torque_pre
        self.safety_factor = safety_factor
        self.stress_yield = stress_yield
        self.stiffness = stiffness
        self.unutilized_elasticity = unutilized_elasticity
        self.torque_pre_max = torque_pre_max

    def __repr__(self):
        if round(self.unutilized_elasticity) == 0:
            return [
                print(''),
                print('Properties:'),
                print(f'Elasticity: {round(self.elasticity, 2)}MPa'),
                print(f'Yield stress: {round(self.stress_yield, 2)}MPa'),
                print(f'Safety factor: {self.safety_factor}'),
                print(f'Stiffness: {round(self.stiffness, 2)}Nmm/rad'),
                print(f'Outer radius at preload: {round(self.radius_pre, 2)}mm'),
                print(f'Arclength of spring: {round(self.arclength_E, 2)}mm'),
                print(f'Range of motion: {self.deltatheta_opt}rad'),
                print(f'Preload torque: {self.torque_pre}Nmm'),
                print(''),
                print('Physical Dimensions (output to CAD):'),
                print(f'Height: {self.height}mm'),
                print(f'Thickness: {round(self.thickness, 2)}mm'),
                print(f'Center pad radius: {self.radius_center}mm'),
                print(f'Minimum coil distance: {self.pitch_0}mm'),
                print(f'Pitch @ rest: {round(self.pitch_R, 2)}mm'),
                print(f'Revolutions at rest: {round(self.number_revolutions, 2)}'),
            ]
        else:
            return [
                print(''),
                print('Properties:'),
                print(f'Elasticity: {round(self.elasticity, 2)}MPa'),
                print(f'Yield stress: {round(self.stress_yield, 2)}MPa'),
                print(f'Safety factor: {self.safety_factor}'),
                print(f'Stiffness: {round(self.stiffness, 2)}Nmm/rad'),
                print(f'Outer radius at preload: {round(self.radius_pre, 2)}mm'),
                print(f'Arclength of spring: {round(self.arclength_E, 2)}mm'),
                print(f'Range of motion: {self.deltatheta_opt}rad'),
                print(f'Preload torque: {self.torque_pre}Nmm'),
                print(''),
                print('Physical Dimensions (output to CAD):'),
                print(f'Height: {self.height}mm'),
                print(f'Thickness: {round(self.thickness, 2)}mm'),
                print(f'Center pad radius: {self.radius_center}mm'),
                print(f'Minimum coil distance: {self.pitch_0}mm'),
                print(f'Pitch @ rest: {round(self.pitch_R, 2)}mm'),
                print(f'Revolutions at rest: {round(self.number_revolutions, 2)}'),
                print(''),
                print(f'This spring leaves {round(self.unutilized_elasticity, 2)}MPa of elasticity unutilized!'),
                print(f'Increase preload torque to {round(self.torque_pre_max, 2)}Nmm to fully utilize elasticity.')
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
        stiffness = -fopt
        radius_E =(
            cls.calculate_radius_E(thickness, radius_center, pitch_0))
        deltatheta_R =(
            cls.calculate_deltatheta_R(height, elasticity, thickness, arclength_E, deltatheta_opt, torque_pre))
        theta_EMD =(
            cls.calculate_theta_EMD(arclength_E, thickness, radius_E, pitch_0))
        radius_pre =(
            cls.calculate_radius_pre(arclength_E, theta_EMD, deltatheta_opt, radius_E))
        theta_E =(
            cls.calculate_theta_E(theta_EMD, deltatheta_R))
        radius_R =(
            cls.calculate_radius_R(arclength_E, theta_E, radius_E))
        pitch_R =(
            cls.calculate_pitch_R(radius_R, radius_E, theta_E))
        number_revolutions =(
            cls.calculate_number_revolutions(theta_E))
        stress_max =(
            cls.calculate_stress_max(thickness, deltatheta_R, arclength_E, elasticity))
        unutilized_elasticity =(
            cls.calculate_unutilized_elasticity(safety_factor, stress_yield, stress_max))
        torque_pre_max =(
            cls.calculate_torque_pre_max(
                height, thickness, arclength_E, safety_factor, stress_yield, elasticity, deltatheta_opt))

        #create instance:
        return cls(height, thickness, radius_center, pitch_0, pitch_R, number_revolutions,
                   arclength_E, elasticity, radius_pre, deltatheta_opt, torque_pre, safety_factor,
                   stress_yield, stiffness, unutilized_elasticity, torque_pre_max)

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
        radius_E =(
            SpiralTorsionSpring.calculate_radius_E(thickness, radius_center, pitch_0))
        deltatheta_R =(
            SpiralTorsionSpring.calculate_deltatheta_R(
                height, elasticity, thickness, arclength_E, deltatheta_opt, torque_pre))
        theta_EMD =(
            SpiralTorsionSpring.calculate_theta_EMD(arclength_E, thickness, radius_E, pitch_0))
        stress_max =(
            SpiralTorsionSpring.calculate_stress_max(thickness, deltatheta_R, arclength_E, elasticity))
        radius_pre =(
            SpiralTorsionSpring.calculate_radius_pre(arclength_E, theta_EMD, deltatheta_opt, radius_E))
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

    @staticmethod
    def calculate_unutilized_elasticity(
            safety_factor, stress_yield, stress_max):
        return safety_factor * stress_yield - stress_max

    @staticmethod
    def calculate_torque_pre_max(
            height, thickness, arclength_E, safety_factor, stress_yield, elasticity, deltatheta_opt):
        return (((height * thickness ** 2 * 2 * arclength_E * safety_factor * stress_yield)
                - (elasticity * height * thickness ** 3 * deltatheta_opt))
                / (12 * arclength_E))

if __name__ == '__main__':
    input_height = 4
    input_elasticity = 3100
    input_max_radius_pre = 25
    input_radius_center = 8
    input_pitch_0 = 0.5
    input_deltatheta_opt = 6
    input_torque_pre = 10
    input_safety_factor = .75
    input_stress_yield = 83
    input_max_thickness = 4
    input_nozzle_diameter = 0.4
    spring = SpiralTorsionSpring.maximize_stiffness(
        input_height, input_elasticity, input_max_radius_pre, input_radius_center, input_pitch_0,
        input_deltatheta_opt, input_torque_pre, input_safety_factor, input_stress_yield,
        max_thickness=input_max_thickness, nozzle_diameter=input_nozzle_diameter
    )
    spring.__repr__()
