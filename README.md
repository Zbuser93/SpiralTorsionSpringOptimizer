# Spiral-Torsion-Spring Optimizer

For the fully-functional spreadsheet-based version of this project, see the page on [Printables](https://www.printables.com/model/485731-spiral-torsion-spring-optimizer-v3).

## Introduction

A spiral torsion spring (STS) is a spring that occupies a cylindrical volume and has an angular range of motion (ROM) around the center axis of that cylinder. In this project I use the term "height" to refer to the dimension of the spring that is parallel with the cylinder center axis, and the term "thickness" to refer to the dimension that runs perpendicular to the spiral tangent. There are several potential optimization goals one might have in designing an STS, for instance, one might want to find:
1. the maximum thickness under height, radius, and ROM constraints
2. the minimum height under stiffness, radius, and ROM constraints
3. the minimum radius under height, stiffness and ROM constraints.
4. the maximum ROM under stiffness, height, and radius constraints.

Currently, this project only supports goal 1, though I do plan to support all possible optimization goals in the future. All of these optimization goals would also be subject to general feasibility constraints, for instance, the spring must stay within its material's elastic zone at the end of its range of motion.
The problem becomes a little more complicated when we add in more spring parameters that a designer might require, such as the spring's preload torque and the distance between spring coils at the end of its ROM (so the spring does not collide with itself). Let's define some possible states for our spring:
1. Rest state
   - The spring with zero angular force applied. This is the state the spring will be in before it is assembled into the host device, and how the spring will be printed if it is to be made by 3D-printing.
2. Preload state
   - The spring at rest within its host device. If no preload torque is desired, this will be the same as the rest state. If preload torque is set higher than zero, then some force is applied to the spring during assembly, and therefore the spring applies a non-zero torque to its host device at all times. The ROM of the spring is the angular distance between the preload state and MD, not the rest state and MD.
3. Maximum deformation (MD) state
   - The spring at the very end of its useful ROM. This may not be as far as the spring can physically be deformed. This tool will require that the spring stays within its material's elastic zone at this state. If we want the spring to stop before it collides with itself (for instance, to avoid the resulting friction) then we must create another parameter of minimum coil distance. This parameter may sound innocuous, but in reality even at low values it can have an enormous effect on the spring's pitch.
4. End state
   - This is the spring deformed or twisted as far as it possibly can be, where the spring coils have collided with eachother and stopped any further deformation. This may be the same as the closed state if no minimum coil distance is set. This tool will not require that the spring stay within its elastic zone at the spring's end state, so pushing the spring past it's closed state may result in permanent damage to the spring. Therefore it is advisable to design the host device so that it either physically stops the spring from going past MD, or so that it would otherwise not be possible for the spring to exceed MD in normal operation.

There are many properties to a spiral torsion spring. Depending on the optimization goal, some will be inputs, some will be outputs, and some intermediary calculations. Of the inputs, some are material properties, and some will either be variables or "settings" (essentially constraints) depending on the optimization goal. In the case of goal 1 (maximizing stiffness), the properties are organized as follows:

[Diagram](/Images/DiagramMaxStiffness.png)

1. _r<sub>max</sub>_
   -The maximum allowable radius of the spring. Measured from origin to the middle of the end of the spring (does not account for spring thickness).
2. _r<sub>C</sub>_
   -The radius of the center pad of the spring (the part which connects to or contains the center axle).
3. _p<sub>0</sub>_
   -The distance between spring coils at MD.
4. _Δθ<sub>opt</sub>_
   -Desired range of motion of the spring from preload state to MD.
5. _τ<sub>pre</sub>_
   -Amount of torque exerted by spring at preload state.
6. _t_
   -Spring thickness
7. _h_
   -Spring height (z-axis print height if 3D printing).
8. _L<sub>E</sub>_
   -Arclength of the effective portion of the spring
9. _E_
   -Elasticity of the material (Young's modulus)
10. _σ<sub>y</sub>_
   -Material's yield stress
11. _δ_
   -Safety factor (maximum portion of yield stress to be used)



## Current State of the Project

Currently the script will sucessfully optimize a spring using pyswarm, however you have to somewhat tediously type in the inputs by manually changing the variables. The next step will be to create a GUI that takes the inputs from the user, and a macro for FreeCAD that uses this script to automatically generate the spring.
