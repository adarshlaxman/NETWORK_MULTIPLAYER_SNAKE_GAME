import pygame
import socket
import pickle
import threading
from pygame.math import Vector2

class Client:
    def __init__(self):
        pygame.init()
        self.cell_size = 20
        self.cell_number = 40
        self.screen = pygame.display.set_mode((self.cell_number * self.cell_size, self.cell_number * self.cell_size))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 25)
        self.small_font = pygame.font.SysFont('arial', 20)
        
        self.game_state = None
        self.player_num = None
        self.player_color = None
        self.running = True

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        
        # Receive initial player info
        data = pickle.loads(self.socket.recv(1024))
        self.player_num = data['player_num']
        self.player_color = data['color']
        
        # Start thread to receive game updates
        threading.Thread(target=self.receive_updates, daemon=True).start()

    def receive_updates(self):
        while self.running:
            try:
                data = self.socket.recv(4096)
                if data:
                    self.game_state = pickle.loads(data)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    def send_direction(self, direction):
        try:
            self.socket.send(pickle.dumps(direction))
        except Exception as e:
            print(f"Error sending direction: {e}")

    def render_game(self):
        if not self.game_state or 'snakes' not in self.game_state:
            return
            
        self.screen.fill((175, 215, 70))
        
        # Draw snakes (body, color, alive)
        for i, snake_data in enumerate(self.game_state['snakes']):
            snake_body, snake_color, snake_alive = snake_data
            for block in snake_body:
                block_rect = pygame.Rect(int(block.x * self.cell_size), int(block.y * self.cell_size), 
                                       self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, snake_color, block_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), block_rect, 1)
            
            # Highlight your snake's head
            if i == self.player_num - 1:
                head = snake_body[0]
                head_rect = pygame.Rect(int(head.x * self.cell_size), int(head.y * self.cell_size), 
                                      self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (255, 255, 0), head_rect, 3)  # Yellow border for your snake
        
        # Draw food
        if 'food' in self.game_state and self.game_state['food']:
            food_rect = pygame.Rect(int(self.game_state['food'].x * self.cell_size), 
                                  int(self.game_state['food'].y * self.cell_size), 
                                  self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, (255, 0, 0), food_rect)
        
        # Draw scores and player info
        if 'scores' in self.game_state and len(self.game_state['scores']) >= 2:
            score_text = self.font.render(f"Player 1: {self.game_state['scores'][0]} | Player 2: {self.game_state['scores'][1]}", 
                                         True, (0, 0, 0))
            self.screen.blit(score_text, (10, 10))
            
            # Display which player you are
            player_text = self.small_font.render(f"You are Player {self.player_num}", True, self.player_color)
            self.screen.blit(player_text, (10, 40))
        
        # Draw countdown or winner
        if 'countdown' in self.game_state:
            countdown_text = self.font.render(f"Starting in {self.game_state['countdown']}", True, (0, 0, 0))
            self.screen.blit(countdown_text, (self.cell_number * self.cell_size // 2 - 70, 
                                            self.cell_number * self.cell_size // 2))
        elif not self.game_state.get('running', True) and 'winner' in self.game_state:
            if self.game_state['winner'] == 0:
                winner_text = self.font.render("Game Over! It's a tie!", True, (0, 0, 0))
            else:
                winner_text = self.font.render(f"Player {self.game_state['winner']} wins!", True, (0, 0, 0))
            self.screen.blit(winner_text, (self.cell_number * self.cell_size // 2 - 100, 
                                         self.cell_number * self.cell_size // 2))

    def render(self):
        self.render_game()
        pygame.display.update()
        self.clock.tick(60)

    def run(self, host, port):
        self.connect(host, port)
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.send_direction(Vector2(0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.send_direction(Vector2(0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.send_direction(Vector2(-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.send_direction(Vector2(1, 0))
            
            self.render()
        
        pygame.quit()
        self.socket.close()

if __name__ == "__main__":
    HOST = '192.168.160.79'  
    PORT = 5002
    
    client = Client()
    client.run(HOST, PORT)