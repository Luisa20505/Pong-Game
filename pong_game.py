#Implementation von Pong mithilfe von Pygame
#Authors: Jonas Gießler, Luisa Gaiser
#Bild und Soundquellen siehe contributions.txt
#Wie Besprochen, sind die Klassen Player und AI Player nicht einzeln umgesetzt

import pygame
import sys
import random
import math
import os


pygame.init()
info_object = pygame.display.Info()
screen_size = (info_object.current_w, info_object.current_h)
radius = 30
background_color = (20, 20, 20)

class Paddle:
    #A class defining the Paddles
    def __init__(self, x:int, y:int, width:int, height:int, speed:int):
        """define the paddle and its dimensions.
        
        x: X-koordinate of the paddle.
        y: Y-koordinate of the paddle.
        width: (horizontal) width of the paddle (in px).
        height: (vertical) height of the paddle (in px).
        speed: maximum speed of the paddle (in px per frame).
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.speed = speed

    def draw(self, display:pygame.display):
        """draws the paddle.
        display: the pygame instance of the display to draw on"""
        pygame.draw.rect(display, self.color, self.rect)

    def move(self, up:bool, down:bool):
        """function to move the paddles.
        
        up: if paddle is to move up.
        down: if paddle is to move down."""
        if up and self.rect.top > 0:
            self.rect.move_ip(0, -self.speed*gs.dt_last_frame)
        if down and self.rect.bottom < screen_size[1]:
            self.rect.move_ip(0, self.speed*gs.dt_last_frame)
   
class Ball:
    #defines an instance of a the ball
    def __init__(self, x, y, radius, speed):
        """define the ball and its dimensions.
        
        x: X-koordinate of the ball
        y: Y-koordinate of the ball
        radius: radius of the ball
        speed: base-speed of the ball (in px per frame at 60 fps)
        """
        self.rect = pygame.Rect(x, y, radius*2, radius*2)
        self.speed = [speed * random.choice((-1, 1)), speed * random.choice((-1, 1))]
        self.speed = [speed * random.choice((-1.5, 1.5)), speed * random.choice((-1, 1))]

        self.image = pygame.image.load('Bilder/Ball/0SoccerBall.png') 
        self.image = pygame.transform.scale(self.image, (radius*2, radius*2))  

    def draw(self, display:pygame.display):
        """draws the ball onto the frame.
        
        display: instance of the display the ball should be drawn too."""
        display.blit(self.image, self.rect)  # Zeichnen des Bildes anstatt der Ellipse

    def move(self, speed_inc):
        """function to move the ball, including colission with playfield-boundries."""
        
        if self.rect.top < 0:
            if self.speed[1] < 0:
                self.speed[1] = -self.speed[1]
                if gs.game_started:
                    pygame.mixer.Sound.play(gs.bounce)
            
        if self.rect.bottom > screen_size[1]:
            if self.speed[1] > 0:
                self.speed[1] = -self.speed[1]
                if gs.game_started:
                    pygame.mixer.Sound.play(gs.bounce)
        self.rect.move_ip([speed * speed_inc *gs.dt_last_frame for speed in self.speed])

class Obstacle:   
    #defines a new obstacle
    def __init__(self, x, y, width, height):
        """define the obsticle and its dimensions.
        
        x: X-koordinate of the obstacle.
        y: Y-koordinate of the obstacle.
        width: (horizontal) width of the obstacle (in px).
        height: (vertical) height of the obstacle (in px).
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def draw(self, display:pygame.display):
        """draws the paddle.
        display: the pygame instance of the display to draw on."""
        pygame.draw.rect(display, self.color, self.rect)

    def collide_with(self, ball:Ball):
        """handles the colission of the ball with the obstacle.
        
        ball: class: Ball"""
        dx = (ball.rect.centerx - self.rect.centerx) / self.rect.width
        dy = (ball.rect.centery - self.rect.centery) / self.rect.height
        if abs(dx) > abs(dy):
            if dx > 0: 
                ball.speed[0] = abs(ball.speed[0])
            else: 
                ball.speed[0] = -abs(ball.speed[0])
        else:
            if dy > 0: 
                ball.speed[1] = abs(ball.speed[1])
            else: 
                ball.speed[1] = -abs(ball.speed[1])

class Particle:
    # defines small particle box
    def __init__(self, x, y):
        """defines a new particle.
        
        x: X-koordinate of the particle.
        
        y: Y-koordinate of the particle."""
        self.rect = pygame.Rect(x, y, 5, 5)
        angle = math.pi * random.uniform(0,2)
        rand_speed = random.uniform(0,10)
        self.speed = [rand_speed * math.cos(angle), rand_speed * math.sin(angle)] 
        self.color = (255, random.randint(0,100), 0) 
        self.life = random.randint(50, 100)

    def update(self):
        """called when position of the particle is to be updated"""
        self.rect.move_ip((self.speed[0]*gs.dt_last_frame,self.speed[1]*gs.dt_last_frame))
        self.life -= 1.5*gs.dt_last_frame
    
    def draw(self, display):
        """draws the paddle.
        display: the pygame instance of the display to draw on."""
        pygame.draw.rect(display, self.color, self.rect)

class Trace_particle():
    #defines the trace-particle class
    def __init__(self,x,y):
        """defines a new particle.
        
        x: X-koordinate of the particle.
        
        y: Y-koordinate of the particle."""
        self.rect = pygame.Rect(x, y, 5, 5)
        self.speed = [0, 0]  # derive x and y speed from angle
        self.color = (255, random.randint(0,100), 0) 
        self.life = random.randint(30,80)

    def update(self):
        """called when position of the particle is to be updated"""
        self.rect.move_ip((self.speed[0]*gs.dt_last_frame,self.speed[1]*gs.dt_last_frame))
        self.life -= 1.0*gs.dt_last_frame
    
    def draw(self, display):
        """draws the paddle.
        display: the pygame instance of the display to draw on."""
        pygame.draw.rect(display, self.color, self.rect)

class PulsatingText:

    Texts = []
    def __init__(self, display, text, center, font_size=36):
        """defines a new pulsating text.
        
        display: pygame instance of the display to draw on.
        text: text the pulsating text should display in game.
        center: list(x-position, y-positio).
        fint_size: default = 36px."""
        self.display = display
        self.text = text
        self.center = center
        self.font_size = font_size
        self.phase = 0
        PulsatingText.Texts.append(self)

    def update(self):
        """updates the phase of the blink."""
        self.phase = (self.phase + 0.04*gs.dt_last_frame) % (2 * math.pi)

    def draw(self):
        """draws the Text on the display"""
        pulse_val = abs(math.sin(self.phase)) 
        pulse_color = (pulse_val * 255, pulse_val * 255, pulse_val * 255)
        font = pygame.font.SysFont(None, self.font_size) 
        rendered_text = font.render(self.text, True, pulse_color)
        text_rect = rendered_text.get_rect(center=self.center)
        self.display.blit(rendered_text, text_rect)
            
class Slider():
    def __init__(self, display, x, y, width, height, color, min_val, max_val, start_val):
        """defines an instance of a Slider. 
        
         display: pygame instance of the display to draw on.
         x,y: x- and y coordinates of the slider.
         width: width of the slider.
         height: height of the slider.
         color: color of the slider (R,G,B).
         min_val: minimum value.
         max_value: maximum value.
         start_val: presest starting value.
        """
        self.display = display
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color 
        self.min_val = min_val
        self.max_val = max_val
        self.start_val = start_val
        self.current_val = start_val
        self.rect = pygame.Rect(x, y, width, height)
        self.dragging = False
        self.dragging_pos = 0
    
    def draw(self):
        """draws the paddle."""
        pygame.draw.rect(self.display, self.color, self.rect)
        pygame.draw.rect(self.display, (0, 0, 0), self.rect, 2)
        pygame.draw.rect(self.display, (255, 255, 255), (self.x + self.current_val/self.max_val * self.width - 5, self.y - 5, 10, self.height + 10), 2)
        font = pygame.font.SysFont(None, 36)
        text = font.render(str(self.current_val), True, (255, 255, 255))
        self.display.blit(text, (self.x + self.current_val/self.max_val * self.width - 10, self.y + self.height + 10))
    
    def check_input(self, events):
        """checks the inputs to the slider.
        events: pygame.event"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos): 
                    self.dragging = True
                    self.dragging_pos = mouse_pos[0] - self.x
                    self.current_val = (mouse_pos[0] - self.x) / self.width * self.max_val
                    self.current_val = int(max(self.min_val, min(self.current_val, self.max_val)))
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                if self.dragging: 
                    pygame.mixer.Sound.play(gs.click_sound)
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    mouse_pos = pygame.mouse.get_pos()
                    self.current_val = (mouse_pos[0] - self.x) / self.width * self.max_val
                    self.current_val = int(max(self.min_val, min(self.current_val, self.max_val)))


class Startmenu():
    def __init__(self, display):
        """defines a new startmenu.

        display: instance of the display to draw on."""
        self.selected_gamemode = 'AI'
        self.display = display
        folder_path_balls = "Bilder/Ball"
        self.ball_options = []
        self.index = 0
        self.font_size = 25
        self.font = pygame.font.SysFont(None, self.font_size) 
        self.color_l = (0,0,0)
        self.color_r = (0,0,0)
        y = 200
        self.slider1 = Slider(display, screen_size[0]//2 - 80, y+220, 200, 10, (255, 255, 255), 0, 255, random.randint(20, 255))
        self.slider2 = Slider(display, screen_size[0]//2 - 80, y+270, 200, 10, (255, 255, 255), 0, 255, random.randint(20, 255))
        self.slider3 = Slider(display, screen_size[0]//2 - 80, y+320, 200, 10, (255, 255, 255), 0, 255, random.randint(20, 255))

        self.slider_r_1 = Slider(display, screen_size[0]//2 - 100, y+420, 200, 10, (255, 255, 255), 0, 255, random.randint(20, 255))
        self.slider_r_2 = Slider(display, screen_size[0]//2 - 100, y+470, 200, 10, (255, 255, 255), 0, 255, random.randint(20, 255))
        self.slider_r_3 = Slider(display, screen_size[0]//2 - 100, y+520, 200, 10, (255, 255, 255), 0, 255, random.randint(20, 255))

        for filename in os.listdir(folder_path_balls):
            # Stellt den vollständigen Pfad zur Datei her
            filepath = os.path.join(folder_path_balls, filename)

            # Überprüft, ob die Datei eine Bilddatei ist (z.B. endet auf .png)
            if filepath.endswith((".png", ".jpg", ".jpeg")):
                # Lädt das Bild und fügt es zur Liste hinzu
                image = pygame.image.load(filepath)
                image = pygame.transform.scale(image, (radius*4, radius*4)) 
                self.ball_options.append(image)
        
        PulsatingText(display, "Press Spacebar To Play", (screen_size[0]//2, 3*screen_size[1]//4+100), 36)


    def draw(self):
        """draws the startmenue to the display"""
        x = screen_size[0]//2
        y = 200
        # Links-Dreieck (Pfeil)
        pygame.draw.polygon(self.display, (255, 0, 0), ((x-75-radius, y), (x-radius-50, y-15), (x-radius-50, y+15)))
        # Rechts-Dreieck (Pfeil)
        pygame.draw.polygon(self.display, (255, 0, 0), ((x+75+radius, y), (x+radius+50, y-15), (x+radius+50, y+15)))
        
        # Ausgewählten Ball zeichnen
        ball_image = self.ball_options[self.index]
        self.display.blit(ball_image, (x-radius*2, y-radius*2))

        # Text für die aktuelle Auswahl zeichnen
        text = self.font.render(f"{self.index + 1}/{len(self.ball_options)}", True, (255, 255, 255))  # Weißer Text
        self.display.blit(text, (x-15, y+radius+75))  # Wählen Sie eine geeignete Position

        # Text für Gamemodeauswahl zeichnen (Spiel läuft im Hintergrund im Lazy-Modus)
        text = self.font.render(f"Gamemode: {self.selected_gamemode}", True, (255, 255, 255))
        self.display.blit(text, (x-15, y+radius+100))

        #zeichnet Feld für Gamemodeauswahl
        if(self.selected_gamemode == 'AI'):
            #draw small rectangle on the left side inside the gamemode rectangle
            pygame.draw.rect(self.display, (255, 0, 0), (x-85-radius, y+125, 30, 20), 0)
        elif(self.selected_gamemode == 'PVP'):
            #draw small rectangle on the right side inside the gamemode rectangle
            pygame.draw.rect(self.display, (255, 0, 0), (x-55-radius, y+125, 30, 20), 0)
        
        pygame.draw.rect(self.display, (127, 0, 0), (x-90-radius, y+120, 70, 30), 2)

        # draws a paddle to select its colors
        text = self.font.render(f"Farbauswahl links:", True, (255, 255, 255))  # Weißer Text
        self.display.blit(text, (x-60, y+180))  # Wählen Sie eine geeignete Position
        pygame.draw.rect(self.display, self.color_l, (x-120, y+200, 15, 150), 0)
        self.slider1.draw()
        self.slider2.draw()
        self.slider3.draw()
        if(self.selected_gamemode == 'PVP'):
            text = self.font.render(f"Farbauswahl rechts:", True, (255, 255, 255))  # Weißer Text
            self.display.blit(text, (x-60, y+380))  # Wählen Sie eine geeignete Position
            pygame.draw.rect(self.display, self.color_r, (x+120, y+400, 15, 150), 0)
            self.slider_r_1.draw()
            self.slider_r_2.draw()
            self.slider_r_3.draw()


    def next_ball(self):
        # Vorherigen Ball auswählen
        self.index += 1
        if self.index >= len(self.ball_options):
            self.index = 0
        pygame.mixer.Sound.play(gs.click_sound)

    def prev_ball(self):
        # Nächsten Ball auswählen
        self.index -= 1
        if self.index < 0:
            self.index = len(self.ball_options) - 1
        pygame.mixer.Sound.play(gs.click_sound)

    def next_gamemode(self):
        # Vorherigen Gamemode auswählen
        if self.selected_gamemode == 'AI':
            self.selected_gamemode = 'PVP'
        elif self.selected_gamemode == 'PVP':
            self.selected_gamemode = 'AI'
        pygame.mixer.Sound.play(gs.click_sound)

        
    def check_input(self, events):
        """checks input to the startmenue.
        events: pygame.event"""
        x = screen_size[0]//2
        y = 200
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if pygame.Rect(x-radius-85, y-30, radius+40, 70).collidepoint(mouse_pos): 
                    self.prev_ball()
                elif pygame.Rect(x+radius+5, y-30, radius+60, 70).collidepoint(mouse_pos): 
                    self.next_ball()
                elif pygame.Rect(x-85-radius, y+100, radius+40, 70).collidepoint(mouse_pos): 
                    self.next_gamemode()
        self.slider1.check_input(events)
        self.slider2.check_input(events)
        self.slider3.check_input(events)
        self.set_color_left_paddle()
        if(self.selected_gamemode == 'PVP'):
            self.slider_r_1.check_input(events)
            self.slider_r_2.check_input(events)
            self.slider_r_3.check_input(events)
        self.set_color_right_paddle()

        
    
    def get_curr_im(self) -> pygame.image:
        """returns current selected image of the ball."""
        image = self.ball_options[self.index]
        image = pygame.transform.scale(image, (radius*2, radius*2)) 
        return image
    
    def get_curr_gamemode(self) -> str:
        return self.selected_gamemode
    
    def set_color_left_paddle(self):
        color = (self.slider1.current_val, self.slider2.current_val, self.slider3.current_val)
        self.color_l = color
        gs.paddle1.color = color
    
    def set_color_right_paddle(self):
        color = (self.slider_r_1.current_val, self.slider_r_2.current_val, self.slider_r_3.current_val)
        self.color_r = color
        gs.paddle2.color = color
    
        





class GameState():
    def __init__(self) -> None:
        self.game_started = False
        self.particles: list = []
        pygame.mixer.init()
        pygame.mixer.music.load("Sounds/music-background.mp3") 
        pygame.mixer.music.play(-1,0.0)

        self.explosion = pygame.mixer.Sound("Sounds/explosion.mp3")
        self.explosion.set_volume(0.1)
        self.bounce = pygame.mixer.Sound("Sounds/bounce.wav")
        self.bounce.set_volume(0.7)
        self.click_sound = pygame.mixer.Sound("Sounds/click.wav")
        self.click_sound.set_volume(0.3)

        # spiel läuft bis zu dieser Punktzahl, anfangs auf 100, damit die Paddles bei Start im Hintergrund lange spielen
        self.game_length = 100

        self.display = pygame.display.set_mode(screen_size, pygame.FULLSCREEN | pygame.SCALED, vsync=True)
        #initialisiert die obstacles
        self.obstacles = [Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), random.randint(50,150), random.randint(50,150)) for i in range(0,2)]
        self.FPS = pygame.time.Clock()
        self.speed_increment = 1
        self.paddle1 = Paddle(50, screen_size[1]//2 - 175, 15, 150, 12)
        self.paddle2 = Paddle(screen_size[0]-65, screen_size[1]//2 - 175, 15, 150, 12)
        self.ball = Ball(screen_size[0]//2, screen_size[1]//2, radius, 6)
        self.score = [0, 0]
        self.running = True
        self.dt_last_frame = 1

        self.trace: list = []
        self.MAX_SPEED_SQ = 500
        self.gamemode = "LAZY" #'LAZY' für PC vs. PC, 'AI' für Spieler vs. Computer und 'PVP'.

        self.do_on_end_bool = True

        self.start_menu = Startmenu(self.display)

    def draw_crown(self, pos):
        x = pos[0]-20
        y = pos[1]
        pygame.draw.polygon(self.display, (255, 223, 0), [(x, y), (x - 10, y + 25), (x + 10, y + 25)])
        x += 10
        pygame.draw.polygon(self.display, (255, 223, 0), [(x, y), (x - 10, y + 25), (x + 10, y + 25)])
        x += 10
        pygame.draw.polygon(self.display, (255, 223, 0), [(x, y), (x - 10, y + 25), (x + 10, y + 25)])
        x += 10
        pygame.draw.polygon(self.display, (255, 223, 0), [(x, y), (x - 10, y + 25), (x + 10, y + 25)])
        x += 10
        pygame.draw.polygon(self.display, (255, 223, 0), [(x, y), (x - 10, y + 25), (x + 10, y + 25)])

    def draw_winner_name(self, winner_paddle):
        font = pygame.font.SysFont(None, 72, bold=True) 
        text = font.render("Player " + str(self.score.index(max(self.score[0], self.score[1]))+1) + " Wins!", True, (255, 223, 0))
        text_rect = text.get_rect(center=(screen_size[0]//2, screen_size[1]//4))
        pygame.draw.rect(self.display, winner_paddle.color, text_rect, 2)
        self.display.blit(text, text_rect)

    def game_ended_animation(self):
        #bewegt das gewinner-Paddle in die Mitte des Bildschirms
        winner_paddle = self.paddle1 if self.score.index(max(self.score[0],self.score[1])) == 0 else self.paddle2
        x_delta = winner_paddle.rect.centerx - screen_size[0]//2
        y_delta = winner_paddle.rect.centery - screen_size[1]//2
        move_by = [0,0]
        move_speed = 10.0*gs.dt_last_frame
        if abs(x_delta) > 10:
            move_by[0] = -1.0 * move_speed if x_delta > 0 else move_speed
        if abs(y_delta) > 10:
            move_by[1] = -1.0 * move_speed if y_delta > 0 else move_speed
        winner_paddle.rect.move_ip(move_by)
        winner_paddle.draw(self.display)
        if abs(x_delta) <= 10 and abs(y_delta) <= 10:
            self.draw_crown((winner_paddle.rect.centerx, winner_paddle.rect.y - 40))
            self.draw_winner_name(winner_paddle)

    def move_players(self):
        keys = pygame.key.get_pressed()
        if(self.gamemode=="PVP"):
            self.paddle1.move(keys[pygame.K_w], keys[pygame.K_s])
            self.paddle2.move(keys[pygame.K_UP], keys[pygame.K_DOWN])
        if(self.gamemode=="AI"):
            self.paddle1.move(keys[pygame.K_w], keys[pygame.K_s])
            if(self.ball.speed[0] > 0 and ((self.ball.rect.centery - self.paddle2.rect.centery) > 20 or (self.ball.rect.centery - self.paddle2.rect.centery) < -20)):
                self.paddle2.move(self.ball.rect.centery < self.paddle2.rect.centery, self.ball.rect.centery > self.paddle2.rect.centery)
        if(self.gamemode=="LAZY"):
            if(self.ball.speed[0] > 0 and ((self.ball.rect.centery - self.paddle2.rect.centery) > 20 or (self.ball.rect.centery - self.paddle2.rect.centery) < -20)):
                self.paddle2.move(self.ball.rect.centery < self.paddle2.rect.centery, self.ball.rect.centery > self.paddle2.rect.centery)
            if(self.ball.speed[0] < 0 and ((self.ball.rect.centery - self.paddle1.rect.centery) > 20 or (self.ball.rect.centery - self.paddle1.rect.centery) < -20)):
                self.paddle1.move(self.ball.rect.centery < self.paddle1.rect.centery, self.ball.rect.centery > self.paddle1.rect.centery)

    def check_paddle_colissions(self):
        # Ball kollidiert mit linkem paddle
        if self.ball.rect.colliderect(self.paddle1.rect) and self.ball.speed[0]<0:
            self.ball.speed[0] = -self.ball.speed[0]
            self.ball.speed[1] = random.randint(-10, 10)
            if gs.game_started:
                pygame.mixer.Sound.play(self.bounce)
        # Ball kollidiert mit rechtem paddle
        if self.ball.rect.colliderect(self.paddle2.rect) and self.ball.speed[0]>0:
            self.ball.speed[0] = -self.ball.speed[0]
            self.ball.speed[1] = random.randint(-10, 10) 
            if gs.game_started:
                pygame.mixer.Sound.play(self.bounce)

    def check_ball_scored(self):
        #Punkt für rechts
        if self.ball.rect.left < -10:
            self.score[1] += 1
            self.particles += [Particle(*self.ball.rect.center) for _ in range(200)]
            if gs.game_started:
                pygame.mixer.Sound.play(self.explosion)
            self.ball.rect.center = (screen_size[0]//2, screen_size[1]//2)
            self.ball.speed = [5 * random.choice((-1.5, 1.5)), 5 * random.uniform(-1, 1)] 
            self.speed_increment = 1
            self.obstacles.pop(0)
            self.obstacles.append(Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), random.randint(50,150), random.randint(50,150)))

        #Punkt für links
        elif self.ball.rect.right > screen_size[0]+10:
            self.score[0] += 1
            self.particles += [Particle(*self.ball.rect.center) for _ in range(300)]
            if gs.game_started:
                pygame.mixer.Sound.play(self.explosion)
            self.ball.rect.center = (screen_size[0]//2, screen_size[1]//2)
            self.ball.speed = [5 * random.choice((-1, 1)), 5 * random.choice((-1, 1))] 
            self.ball.speed = [5 * random.choice((-1.5, 1.5)), 5 * random.choice((-1, 1))] 
            self.speed_increment = 1
            self.obstacles.pop(1)
            self.obstacles.append(Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), random.randint(50,150), random.randint(50,150)))

    def check_colissions_obstacles(self):
        #hindernisse zeichnen und kollision
        for obstacle in self.obstacles:  
            if self.ball.rect.colliderect(obstacle.rect):
                obstacle.collide_with(self.ball)
                if gs.game_started:
                    pygame.mixer.Sound.play(self.bounce)
        
    def dim_screen(self,x):
        dim_surface = pygame.Surface((screen_size))  
        dim_surface.fill((0,0,0)) 
        dim_surface.set_alpha(int(256 * (x/100))) 
        self.display.blit(dim_surface, (0,0))

    def draw_obstacles(self):
        for obstacle in self.obstacles:  
            obstacle.draw(self.display)

    def update_draw_particles(self):
        # update and draw the particles
        for particle in self.particles:
            particle.update()
            particle.draw(self.display)
            if particle.life <= 0:
                self.particles.remove(particle)
        #trace zeichnen und updaten
        for particle in self.trace:
            particle.update()
            particle.draw(self.display)
            if particle.life <= 0:
                self.trace.remove(particle)

    def show_score(self):
        font = pygame.font.Font(None, 46)
        text = font.render("" + str(self.score[0]) + " : " + str(self.score[1]), 1, (255, 255, 255))
        self.display.blit(text, (screen_size[0]//2 -30, 40))

    def increase_speed(self):
        # Quadratisches summe der Geschwindigkeiten
        total_speed = self.ball.speed[0]*self.ball.speed[0]*self.speed_increment + self.ball.speed[1]*self.ball.speed[1]*self.speed_increment
        # Überprüfen, ob die Gesamtgeschwindigkeit den maximalen Wert überschritten hat
        if total_speed < self.MAX_SPEED_SQ:
            self.speed_increment = self.speed_increment + 0.0002*gs.dt_last_frame

    def reset_game(self):
        self.gamemode = self.start_menu.get_curr_gamemode()
        self.score[0] = 0 
        self.score[1] = 0 
        self.obstacles.clear()
        self.paddle1.rect.centerx = 50
        self.paddle2.rect.centerx = screen_size[0]-65
        self.paddle1.rect.centery = screen_size[1]//2
        self.paddle2.rect.centery = screen_size[1]//2
        self.obstacles.append(Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), random.randint(50,150), random.randint(50,150)))
        self.obstacles.append(Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), random.randint(50,150), random.randint(50,150)))
        PulsatingText.Texts.clear()
        self.particles.clear()
        gs.game_started = True
        self.game_length = 5
        self.ball.rect.center = (screen_size[0]//2, screen_size[1]//2)
        self.ball.speed = [5 * random.choice((-1, 1)), 5 * random.choice((-1, 1))] 
        self.ball.speed = [5 * random.choice((-1.5, 1.5)), 5 * random.choice((-1, 1))] 
        self.speed_increment = 1
        self.display.fill((15,15,15))
        self.show_score()
        self.draw_obstacles()
        self.paddle1.draw(self.display)
        self.paddle2.draw(self.display)
        self.ball.image = self.start_menu.get_curr_im()
        self.ball.draw(self.display)
        self.trace.clear()
        pygame.mouse.set_visible(False)
        pygame.display.update()
        pygame.event.pump()
        pygame.time.delay(1500)  
        gs.FPS.tick()
        
if __name__ == '__main__':
    gs = GameState()

trace_counter = 1
# main game loop
while gs.running:
    trace_counter+=gs.dt_last_frame
    if max(gs.score[0], gs.score[1]) < gs.game_length and trace_counter > 1:
        trace_counter = 0
        gs.trace += [Trace_particle(*gs.ball.rect.center)]

    #checkt ob das Spiel beendet wurde
    events = pygame.event.get() 
    for event in events:
        if event.type == pygame.QUIT:
            gs.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gs.running = False
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                if not gs.game_started:
                    gs.reset_game()
                    gs.gamemode = gs.start_menu.get_curr_gamemode()
                if event.key == pygame.K_SPACE and max(gs.score[0], gs.score[1]) >= gs.game_length:
                    gs.reset_game()
                    gs.do_on_end_bool = True


    if max(gs.score[0], gs.score[1]) < gs.game_length:
        gs.move_players()
        gs.check_paddle_colissions()
        gs.check_colissions_obstacles()
        gs.ball.move(gs.speed_increment)
        gs.increase_speed()
        gs.check_ball_scored()
    #bild reseten (entspricht Hintergrundfarbe)
    gs.display.fill((15, 15, 15))
    gs.update_draw_particles()
    gs.show_score()
    gs.draw_obstacles()

    if max(gs.score[0], gs.score[1]) >= gs.game_length:
        gs.dim_screen(60)

    #paddles und ball zeichnen
    gs.paddle1.draw(gs.display)
    gs.paddle2.draw(gs.display)
    if max(gs.score[0], gs.score[1]) < gs.game_length:
        gs.ball.draw(gs.display)
    if max(gs.score[0], gs.score[1]) >= gs.game_length:
        gs.game_ended_animation()
        if gs.do_on_end_bool:
            PulsatingText(gs.display, "Press Spacebar To Continue", (screen_size[0]//2, 3*screen_size[1]//4), 36)
            gs.do_on_end_bool = False

    
    if not gs.game_started:
        gs.dim_screen(70)
        gs.start_menu.check_input(events)
        gs.start_menu.draw()

    for t in PulsatingText.Texts:
        t.update()
        t.draw()
        
    pygame.display.flip()
    #multipliziert mit dt_last_frame wirkt es so, als liefen 60 fps. 
    #Für weicheres zeichnen wird versucht, die FPS zu maximieren ohne Animationen oder Zeitkritische Abläufe zu verändern. 
    gs.dt_last_frame = gs.FPS.tick()/17

    
pygame.quit()
sys.exit()