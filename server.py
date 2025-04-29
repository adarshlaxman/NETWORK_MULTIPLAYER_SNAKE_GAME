import socket
import pickle
import threading
import random
import time 
from pygame.math import Vector2

# Game Constants
WIDTH, HEIGHT = 800, 800
CELL_SIZE = 20
CELL_NUMBER = WIDTH // CELL_SIZE
colors = [(0, 255, 0), (0, 0, 255)]  # Green and Blue

class Snake:
    def __init__(self, color):
        self.body = [Vector2(5, 5), Vector2(4, 5), Vector2(3, 5)]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        self.color = color
        self.score = 0
        self.alive = True

    def move(self):
        if self.alive:
            self.body.insert(0, self.body[0] + self.direction)
            if self.add_segment:
                self.add_segment = False
            else:
                self.body.pop()

    def grow(self):
        self.add_segment = True
        self.score += 1

    def reset(self):
        self.__init__(self.color)

class Food:
    def __init__(self, snakes):
        self.position = self.generate_position(snakes)

    def generate_position(self, snakes):
        while True:
            pos = Vector2(random.randint(0, CELL_NUMBER-1), random.randint(0, CELL_NUMBER-1))
            if all(pos not in snake.body for snake in snakes if snake.alive):
                return pos

class Game:
    def __init__(self):
        self.snakes = []
        self.food = None
        self.running = False
        self.lock = threading.Lock()

    def update(self):
        with self.lock:
            if not self.running: return

            # Move all snakes first
            for snake in self.snakes:
                snake.move()

            # Check collisions and food for each snake
            for snake in self.snakes:
                if not snake.alive:
                    continue
                
                # Check wall collision
                if not (0 <= snake.body[0].x < CELL_NUMBER) or not (0 <= snake.body[0].y < CELL_NUMBER):
                    snake.alive = False
                    continue

                # Check snake collisions
                for other in self.snakes:
                    # Check if head collides with any segment of any snake (including own)
                    if snake.body[0] in other.body[1:]:
                        snake.alive = False
                        break

                # Eat food if alive
                if snake.alive and snake.body[0] == self.food.position:
                    snake.grow()
                    self.food = Food(self.snakes)

            # Check game over condition
            alive_snakes = sum(1 for snake in self.snakes if snake.alive)
            if alive_snakes <= 1:
                self.running = False

    def get_game_data(self):
        return {
            'snakes': [(snake.body, snake.color, snake.alive) for snake in self.snakes],
            'food': self.food.position,
            'scores': [snake.score for snake in self.snakes],
            'running': self.running,
            'alive': [snake.alive for snake in self.snakes]
        }

def handle_client(conn, player_index, game):
    while True:
        try:
            data = conn.recv(1024)
            if data:
                direction = pickle.loads(data)
                with game.lock:
                    if game.snakes[player_index].alive and direction + game.snakes[player_index].direction != Vector2(0, 0):
                        game.snakes[player_index].direction = direction
        except:
            break
    conn.close()

def send_updates(game, connections):
    while True:
        game.update()
        data = game.get_game_data()
        
        if not game.running:
            alive_snakes = [i for i, snake in enumerate(game.snakes) if snake.alive]
            if len(alive_snakes) == 1:
                data['winner'] = alive_snakes[0] + 1  # Player numbers are 1-based
            else:
                # Both died at same time or other conditions, check scores
                if game.snakes[0].score > game.snakes[1].score:
                    data['winner'] = 1
                elif game.snakes[1].score > game.snakes[0].score:
                    data['winner'] = 2
                else:
                    data['winner'] = 0  # Tie

        for conn in connections:
            try:
                conn.send(pickle.dumps(data))
            except:
                pass
        
        time.sleep(0.2)  # 5 updates per second

def main():
    HOST = '192.168.160.79'  # Listen on all interfaces
    PORT = 5002

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(2)
    print("Server started. Waiting for players...")

    game = Game()
    connections = []

    # Accept 2 players
    for i in range(2):
        conn, addr = server.accept()
        print(f"Player {i+1} connected from {addr}")
        snake = Snake(colors[i])
        game.snakes.append(snake)
        conn.send(pickle.dumps({'color': colors[i], 'player_num': i+1}))
        connections.append(conn)
        threading.Thread(target=handle_client, args=(conn, i, game)).start()

    # Start countdown
    for i in range(5, 0, -1):
        for conn in connections:
            conn.send(pickle.dumps({'countdown': i}))
        time.sleep(1)
    
    game.food = Food(game.snakes)
    game.running = True
    print("Game started!")
    
    # Start game update loop
    send_updates(game, connections)

if __name__ == "__main__":
    main()