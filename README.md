# PSI 22/23 - Server for Remote Robot Control

## Project Overview

This project is a server designed to autonomously manage the movement of remote robots. The robots log in to the server, which guides them to the center of a coordinate system (position [0, 0]). Upon reaching the center, the robot must collect a secret item. Each robot starts from random coordinates and must navigate to the target while avoiding obstacles.

The server can manage multiple robots simultaneously and ensures flawless communication using a well-defined protocol.

## Features

- **Robot Management**: The server handles multiple robots at once.
- **Autonomous Navigation**: Robots are guided to the target point at [0, 0].
- **Random Start Points**: Robots start at random coordinates for testing purposes.
- **Obstacle Avoidance**: Robots detect and navigate around obstacles.
- **Secret Retrieval**: Upon reaching the goal, robots collect a secret item.
- **Communication Protocol**: The server and robots communicate through a well-defined protocol, ensuring accurate and efficient navigation.

## System Requirements

- **Python version**: 3.x

## Usage

1. Start the server.
2. Robots will connect to the server automatically from random starting positions.
3. The server will navigate the robots to the center of the coordinate system.
4. Robots will avoid obstacles and collect the secret upon reaching the goal.

## Configuration

- **Starting Coordinates**: Robots are initialized at random positions.
- **Communication Protocol**: The server uses a custom protocol to communicate with robots (details can be found in the protocol documentation).
- **Obstacles**: Obstacles are randomly placed within the grid.
