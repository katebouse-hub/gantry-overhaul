# Grid System

## Overview
    
The Infinity Grid System is a modular and scalable grid system that is popular in the 3D printing community, and we decided to use it for this project.

Grid is made up of 1 inch squares, with the max size we can print being 5 x 5 units (25 squares). This modularity allows us to 
create a zoning system based on what color we print the grid in (see more about zoning below). To pair with this grid, we selected 
a model for shipping containers that also use the Infinity Grid System, with the container sizes being 1 X 2 inches and 1 X 4 inches.

There will also be a queing system for the containers, with the loading zone being the top of the priority queue, and different zones having 
varying priorities (see the camera docs []and below for more info).
## Details 

### Rules 
There are a few rules that we have to follow when using the grid system for this project:


1. Container color / zone color **MUST** match, no exceptions. A box in the wrong zone needs to be picked and placed into the proper area.  
2. Containers in the *loading zone* need to be prioritized, and put into the top of the proirity queue.
3. Containers in the *priority zone* need to be prioritized, and put into the top of the proirity queue (less than loading zone).
4. E-stop stops **ALL** activity (still deciding if we want 2 e stops - 1 for hardstop, 1 for softstop ie put the container down and stop)
5. Colors will be prioritized based on the zones, and then by how long the container has been in the factory/when it is scheduled to leave (see scheduling rules document).

### Zoning 
Here are the zoning colors for the containers (in order of priority) (WIP!):

| Color | Zone |
| ----- | ---- |
| Red | Emergency Zone, Loading Zone |
| Blue | Priority Zone |
| Green | Private Industry Zone |
| Yellow | Commercial Zone |
| Orange | Express Zone |
| Undecided | Consumer Zone | 
| Gray | International Zone |
| Pink | Davis's Special Zone |

#### Emergency Zone / Loading Zone
The red zone is the first zone that the container will be placed in, and is used for the e-stop. This zone will always be prioritized, since it needs to be clear for ships to quickly load/unload and for 
e-stop (soft) scenarios. 

#### Priority Zone
The blue zone is the second zone that the container will be placed in, and is used for the priority queue. Priority queue placement can be for a number of reasons: 
- palceholder

#### Private Industry Zone
The green zone is the third zone that the container will be placed in, and is used for the private industry. Think industrys like oil or computing (anything with big name brand value or significant market value). 
This zone has a high volume of containers in and out of the system (think oil tankers), and is prioritized by the length of time the container has been in the factory/when ship is scheduled (see scheduling rules document).

### Images 
Here are some images of the grid system:

![Grid System](../images/grid.JPG)

![Containers](../images/containers.JPG)

![Containers in the zone](../images/full.JPG)


## Assembly

### Printing

### Assembly



