# AI and Vision
This portion of the code if for the AI and vision system

The subsystems are as follows:

1. Auto 
2. Skynet 
3. WIP

## Auto
Auto is the agentic LLM system that is responsible for controlling and querying the whole system. 

What it can do:
- Control the whole system
    - Soft stop/E-stop the system
    - Start system
- Query the system and data
- Query the environment
- Generate charts

What it cannot do:
- Track containers (done by Skynet)
    - It can only query Skynet for container information 

## Skynet
Skynet is the vision and container tracking system that is responsible for tracking and relaying information about containers to other sub-systems.

What it can do:
- Track containers
- Create mapping of containers to their location on the grid 
- Provide various information about environment to other sub-systems through api endpoints

What it cannot do:
- Control the environment
- Control the LLM
- Perform actions like Auto can

# Vision 
Skynet is the vision and container tracking system that is responsible for tracking and relaying information about containers to other sub-systems. It got its name "Skynet" from 
the movie serires "Terminator" inplying a smart system that can see and track things.

This system requires you to be using the genicam and harvesters to connect to the camera. The Genicam pacakge needs to be installed at a systems level in order to work, and you can then import it into your python env. 
It is not available on aarch64 systems, so it will run on the gantry-server, but not the Odin system (Jetson AGX Thor).

Models being used:
- None currently
- Looking to explore a VLM or YOLO model for object detection

# AI - Agenic LLM
Auto is the agentic LLM system that is responsible for controlling and querying the whole system. The name "Auto" is inspired by the captain from WALL-E, the red stearing wheel who is actively working against WALL-E.

Models being used:
- gpt-oss:120b
  - This is the model that is used for the Auto system.

# WIP

WIP is the work in progress system that is responsible for providing information about the environment to other sub-systems.
  
