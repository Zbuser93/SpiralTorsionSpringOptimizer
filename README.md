# Spiral-Torsion-Spring Optimizer

## Introduction

A spiral torsioin spring (STS) is a spring that occupies a cylindrical volume and has an angular range of motion (ROM) around the center axis of that cylinder. In this project I use the term "height" to refer to the dimension of the spring that is parallel with the cylinder center axis, and the term "thickness" to refer to the dimension that runs perpendicular to the spiral tangent. There are several potential optimization goals one might have in designing an STS; one might want to find:
1. the maximum thickness under height, radius, and ROM constraints
2. the minimum height under stiffness, radius, and ROM constraints
3. the minimum radius under height, stiffness and ROM constraints.
4. the maximum ROM under stiffness, height, and radius constraints.

All of these optimization goals would also be subject to general feasibility constraints; for instance, the spring must stay within its material's elastic zone at the end of it's range of motion.
The problem quickly becomes more complicated when we add in more spring parameters that a designer might require, such as the spring's preload torque, and the distance between spring coils at the end of its ROM (so the spring does not collide with itself). Let's define some possible states for our spring:
1. Rest state
   - The spring with zero angular force applied. This is the state the spring will be in before it is assembled into the host device, and how the spring will be printed if it is to be made by 3D-printing.
2. Open state
   - The spring at rest within its host device. If no preload torque is desired, this will be the same as the rest state. If preload torque is set higher than zero, then some force is applied to the spring during assembly, and therefor the spring applies a non-zero torque to its host device at all times. The ROM of the spring is the angular distance between the open state and closed state, not the rest state and closed state. This means we must optimize the spring at the open state, and treat the desired pre-load torque as a parameter of the spring.
3. Closed state
   - The spring at the very end of its useful ROM. This may not be as far as the spring can physically be deformed. This tool will require that the spring stays within its material's elastic zone at this state. If we want the spring to stop before it collides with itself (for instance, to avoid the resulting friction) then we must create another parameter of minimum coil distance. This parameter may sound innocuous, but in reality even at low values it can have an enormous effect on the spring's pitch. It is advisable to design the host device so that it either physically stops the spring from going past this point, or so that it otherwise would not be possible for the spring to exceed this point in normal operation.
4. Physical maximum deformation state
   - This is the spring deformed or twisted as far as it possibly can be, where the spring coils have collided with eachother and stopped any further deformation. This may be the same as the closed state if no minimum coil distance is set. This tool will not require that the spring stay within its elastic zone at the spring's physical maximum deformation state, so pushing the spring past it's closed state may result in permanent damage to the spring.
