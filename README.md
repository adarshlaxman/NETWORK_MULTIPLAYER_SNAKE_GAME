Snake Game - Server and Client
Overview
This project consists of a multiplayer Snake Game where two players control their respective snakes. The game is played over a network with one server managing the game logic and clients sending their movements. The game features food spawning, snake growth, and player elimination on collision.

Components:
Server (Python) - Manages the game state, handles player connections, and sends game updates to clients.

Client (Python/Pygame) - Displays the game, sends player inputs, and receives game updates from the server.

Requirements
Python:
Python 3.7 or higher

Required libraries: pygame, socket, pickle, threading

You can install the required libraries using pip:

bash
Copy
Edit
pip install pygame
Server (Python)
Description:
The server handles connections from two clients, manages the game state, and sends updates to the clients. It also receives player movements and updates the snake positions accordingly.

How to Run:
Start the server:

bash
Copy
Edit
python server.py
The server listens on IP 192.168.160.79 and port 5002 (or customize as needed).

The server will wait for two clients to connect. After both players have connected, it will start the game with a countdown.

Key Features:
Handles multiple clients (up to 2 players).

Manages the game state (snake positions, food, scores).

Sends periodic updates to clients.

Checks for collisions (snake vs wall or snake vs snake).

Determines a winner based on score or snake survival.

Client (Python/Pygame)
Description:
The client connects to the server, displays the game state, and allows the player to control their snake using arrow keys. It listens for game updates from the server and renders them.

How to Run:
Start the client:

bash
Copy
Edit
python client.py
The client connects to the server at <Server IP> on port 5002.

Note: Replace <Server IP> with the IP address of the machine where the server is running. If the server is running on your local machine, you can use 127.0.0.1 or the local network IP (e.g., 192.168.160.79).

The client will display the game interface and await user input.

Key Features:
Displays the game grid, snakes, food, and scores.

Handles user input (arrow keys) to move the snake.

Displays countdown before the game starts.

Highlights the current player's snake.

Displays the winner at the end of the game.

Game Flow
Server Initialization: The server listens for client connections and waits for two players to join. Once both players are connected, a countdown begins, and the game starts.

Game Loop:

Players can control their snakes using the arrow keys.

The server updates the positions of the snakes, checks for collisions, and handles the game state (food consumption and snake growth).

The game continues until only one snake survives or the game ends in a tie.

Game End: The server determines the winner based on who survived or who has the highest score and sends the result to both clients.

Networking Details
Server:
Host: 192.168.160.79 (replace this with your actual server IP address if needed)

Port: 5002

Connections: The server accepts two client connections.

Client:
The client connects to the server using the specified IP address and port. Once connected, it receives game updates and sends player inputs to the server.

Game Mechanics
Movement: Players control their snakes using the arrow keys. The snakes move one cell at a time.

Growth: Each time a snake eats food, it grows by one segment.

Collision: The game ends for a player if their snake hits the wall or collides with the body of another snake.

Winning: The game ends when only one player’s snake survives, or it can end in a tie if both players die simultaneously. The player with the highest score wins.

Customization
Game Speed: The game updates every 200ms (5 updates per second). You can adjust this by modifying the time.sleep(0.2) in the server code.

Cell Size/Resolution: The grid size and cell size are adjustable in the server and client code.

Colors: You can modify the colors list to change the snake colors in the game.

Troubleshooting
Server not running: Ensure the server is running before starting the client. The server must be listening on the specified IP and port.

Connection issues: Ensure both the server and client are on the same network or adjust IP settings accordingly.
