from pygame import *
import numpy as np
from random import choice
import sys
import cv2
import mediapipe as mp
import threading

# Pong game with mediapipe and opencv python.
# Author: Bogdan Tomasciuc
# Date: 2021-09-26
# Version: 0.1
# Usage: python3 mp-pong.py

# Import the libraries

# Game Class
class MpPong:
    # Game variables
    # Constants
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    PADDLE_WIDTH = 15
    PADDLE_HEIGHT = 150
    BALL_RADIUS = 10
    PADDLE_SPEED = 5
    BALL_SPEED_X = 0
    BALL_SPEED_Y = 5
    # Colors
    PADDLE_COLOR = (255, 255, 255)
    BALL_COLOR = (255, 255, 255)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    CYAN = (0, 255, 255)
    NAVY = (0, 0, 128)
    SILVER = (192, 192, 192)

    # Initialize the game
    def __init__(self):
        # Game settings
        font.init()
        mixer.init()

        self.screen = display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = time.Clock()
        display.set_caption("MpPong")

        mixer.music.load("assets/bg-music-1.mp3")
        mixer.music.play(-1)

        # Game variables
        self.player1 = [50, (self.HEIGHT - self.PADDLE_HEIGHT) // 2]
        self.player2 = [self.WIDTH - 50 - self.PADDLE_WIDTH, (self.HEIGHT - self.PADDLE_HEIGHT) // 2]
        self.ball_pos = [self.WIDTH // 2, self.HEIGHT // 2]
        self.ball_vel = [self.BALL_SPEED_X, self.BALL_SPEED_Y]
        self.player1_score = 0
        self.player2_score = 0
        self.font = font.SysFont("comicsans", 50)

    # Create the paddles
    def paddle(self, player):
        draw.rect(self.screen, self.GREEN, (player[0], player[1], self.PADDLE_WIDTH, self.PADDLE_HEIGHT))

    # Create the ball
    def ball(self, pos):
        draw.circle(self.screen, self.ORANGE, pos, self.BALL_RADIUS)

    # Move the ball
    def move_ball(self):
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
        self.check_collision()
        self.check_paddle_collision()

        if self.ball_pos[0] <= 0 + self.BALL_RADIUS:
            self.player2_score += 1
            self.reset_ball()
        if self.ball_pos[0] >= self.WIDTH - self.BALL_RADIUS:
            self.player1_score += 1
            self.reset_ball()
        self.display_winner()

    # Check the collision with the edges
    def check_collision(self):
        if self.ball_pos[1] <= 0 or self.ball_pos[1] >= self.HEIGHT:
            self.ball_vel[1] = -self.ball_vel[1]

    # Check the collision with the paddles
    def check_paddle_collision(self):
        if self.ball_pos[0] <= self.player1[0] + self.PADDLE_WIDTH and self.player1[1] <= self.ball_pos[1] <= self.player1[
            1] + self.PADDLE_HEIGHT:
            self.ball_vel[0] = -self.ball_vel[0]
        if self.ball_pos[0] >= self.player2[0] and self.player2[1] <= self.ball_pos[1] <= self.player2[
            1] + self.PADDLE_HEIGHT:
            self.ball_vel[0] = -self.ball_vel[0]

    # Reset the ball
    def reset_ball(self):
        self.ball_pos = [self.WIDTH // 2, self.HEIGHT // 2]
        random_direction = choice([1, -1])
        self.ball_vel = [self.BALL_SPEED_X * random_direction, self.BALL_SPEED_Y]

    # Check the winner
    def check_winner(self):
        if self.player1_score == 5:
            return "Player 1"
        if self.player2_score == 5:
            return "Player 2"
        return None

    # Display the winner
    def display_winner(self):
        winner = self.check_winner()
        if winner:
            self.ball_vel = [0, 0]
            self.ball_pos = [self.WIDTH // 2, 50]
            text = self.font.render(f"{winner} wins!", 1, self.WHITE)
            self.screen.blit(text,
                             (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2 - text.get_height() // 2))
            # Restart the game if Y is pressed or quit if N is pressed
            # Ask if the player wants to restart the game
            restart_text = self.font.render("Do you want to play again? (Y/N)", 1, self.PURPLE)
            self.screen.blit(restart_text,
                             (self.WIDTH // 2 - restart_text.get_width() // 2, self.HEIGHT // 2 + 100))
            display.update()
            time.delay(1000)  # Prevent flickering
            # Keyboard restart controls
            keys = key.get_pressed()
            if keys[K_y]:
                self.restart_game()
            if keys[K_n]:
                sys.exit()

    # Restart the game
    def restart_game(self):
        self.player1_score = 0
        self.player2_score = 0
        self.__init__()
        self.run_game()

    # Game loop
    def run_game(self):
        run = True

        # Start palm tracking in a separate thread
        palm_tracking_thread = threading.Thread(target=self.palm_tracking)
        palm_tracking_thread.start()

        while run:
            for e in event.get():
                if e.type == QUIT:
                    run = False
                    sys.exit()
            # Keyboard controls
            keys = key.get_pressed()
            if keys[K_w] and self.player1[1] > 0:
                self.player1[1] -= self.PADDLE_SPEED
            if keys[K_s] and self.player1[1] < self.HEIGHT - self.PADDLE_HEIGHT:
                self.player1[1] += self.PADDLE_SPEED
            if keys[K_UP] and self.player2[1] > 0:
                self.player2[1] -= self.PADDLE_SPEED
            if keys[K_DOWN] and self.player2[1] < self.HEIGHT - self.PADDLE_HEIGHT:
                self.player2[1] += self.PADDLE_SPEED

            self.move_ball()
            self.screen.fill(self.BLACK)
            self.paddle(self.player1)
            self.paddle(self.player2)
            self.ball(self.ball_pos)

            player1_score = self.font.render(str(self.player1_score), 1, self.WHITE)
            player2_score = self.font.render(str(self.player2_score), 1, self.WHITE)

            self.screen.blit(player1_score, (self.WIDTH // 4, 50))
            self.screen.blit(player2_score, (self.WIDTH // 4 * 3, 50))

            display.update()
            self.clock.tick(self.FPS)

    # Palm tracking with mediapipe for alternative controls
    # Register player 1 and player 2 hands and track the palm position
    # Use the palm position to move the paddles
    def palm_tracking(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands

        cap = cv2.VideoCapture(0)
        with mp_hands.Hands(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as hands:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Ignoring empty camera frame.")
                    continue

                frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
                frame.flags.writeable = False
                results = hands.process(frame)

                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        for i, landmark in enumerate(hand_landmarks.landmark):
                            h, w, c = frame.shape
                            cx, cy = int(landmark.x * w), int(landmark.y * h)
                            if i == 8:
                                cv2.circle(frame, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
                                self.player1[1] = cy

                cv2.imshow('MediaPipe Hands', frame)

                if cv2.waitKey(5) & 0xFF == 27:
                    break

        cap.release()


if __name__ == "__main__":
    game = MpPong()
    game.run_game()
