# Shipping Dock Gantry
This project demonstrates a miniature automated shipping dock that integrates PLC controls, ROS2 orchestration, and Ignition SCADA/HMI into a cohesive teaching and research platform.

The dock serves as a modular cell within a larger automated factory line for education, designed to show how industrial automation, robotics, and IIoT systems communicate and coordinate in real-world manufacturing.

## Process Flow Diagram
![System Diagram](docs/images/Gantry_PFD_Poster_5.png)

## 🔑 Features

### PLC Control Layer
Handles hard real-time I/O, safety features.

### ROS2 Integration
Provides orchestration, order handling, and connectivity with external systems using standard ROS2 nodes.

### Machine Vision 
Integrates with a machine vision system to provide real-time object detection, sorting, and tracking.

### Ignition SCADA
Delivers real-time monitoring, alarms, PackML state visualization, production metrics, and operator interaction.

### PackML State Machine
Implements a standardized cell lifecycle (Idle → Starting → Execute → Complete → Reset) for easy line integration.
 
### AI Integration
- Integrates with a machine learning model to provide real-time object detection, sorting, and tracking.
- Interfaces with a Large Language Model to provide natural language command processing capabilities.

### Educational Focus
Built for educational use in University of Idaho Robotics program.

## 🛠 Tech Stack

PLC: Gantry Control

ROS2: Middleware for order management, vision/ID, and system health

Ignition (Inductive Automation): HMI/SCADA, data historian, and IIoT gateway

## 🎯 Goals

1. Provide a hands-on teaching tool for factory automation concepts
2. Demonstrate cross-layer integration (device → orchestration → SCADA)
3. Serve as a modular factory cell that can plug into larger educational factory lines
---

## 📁 Project Structure <br>

project-name/ <br>
├── src/ # Main source code (if applicable) <br>
├── tests/ # Unit tests (if applicable) <br>
├── docs/ # All documentation related to project should go here <br>
├── .gitignore # Git ignore rules <br>
├── README.md # Project overview <br>
├── LICENSE # Optional: Add your preferred license <br>

---

## 🚀 Getting Started

TBD

## 🧪 Usage Examples

TBD

## 📄 License

This project is licensed under the MIT License, but feel free to change it to meet your needs.

## 🤝 Contributing

TBD. Closed project for now.

## 📝 Authors/Roles

**Davis Onyeoguzoro**
- Team leader
- Head of PLC
- Contributer to ROS2 
- Electrical Wiring and Hardware Integration

**James Lasso** 
- Co-leader of ROS2
- Head of Ignition
- Managing Git and GitHub

**Tim Libeck**
- Head of ROS2 
- Co-leader of the PLC unit 
- (more)

**Dawson Burgess**
- Server Administrator
- Head of AI
- Head of Machine Vision
- Contributer to ROS2 

**Dr. John Shovic**
- Big boss

## 📦 Versions
TBD. We're not using versioning yet.
