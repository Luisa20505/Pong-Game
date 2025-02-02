import pygame
import sys
import random
import math
import os

game_started = [False]
pygame.init()
info_object = pygame.display.Info()
screen_size = (info_object.current_w, info_object.current_h)
radius = 30

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
            self.rect.move_ip(0, -self.speed)
        if down and self.rect.bottom < screen_size[1]:
            self.rect.move_ip(0, self.speed)
   
class Ball:
    #defines an instance of a the ball
    def __init__(self, x, y, radius, speed):
        """define the ball and its dimensions.
        
        x: X-koordinate of the ball
        y: Y-koordinate of the ball
        radius: radius of the ball
        speed: base-speed of the ball (in px per frame)
        """
        self.rect = pygame.Rect(x, y, radius*2, radius*2)
        self.speed = [speed * random.choice((-1, 1)), speed * random.choice((-1, 1))]
        self.speed = [speed * random.choice((-1.5, 1.5)), speed * random.choice((-1, 1))]

        self.image = pygame.image.load('Bilder/Ball/SoccerBall.png') 
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
                if game_started[0]:
                    pygame.mixer.Sound.play(gs.bounce)
            
        if self.rect.bottom > screen_size[1]:
            if self.speed[1] > 0:
                self.speed[1] = -self.speed[1]
                if game_started[0]:
                    pygame.mixer.Sound.play(gs.bounce)
        self.rect.move_ip([speed * speed_inc for speed in self.speed])

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
        angle = 2 * math.pi * random.random()  # create a random angle
        self.speed = [(random.random() * 10) * math.cos(angle), (random.random() * 10) * math.sin(angle)]  # derive x and y speed from angle
        self.color = (255, random.randint(0,100), 0) 
        self.life = random.randint(50, 100)

    def update(self):
        """called when position of the particle is to be updated"""
        self.rect.move_ip(self.speed)
        self.life -= 1
    
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
        self.life = random.randint(50, 100)

    def update(self):
        """called when position of the particle is to be updated"""
        self.rect.move_ip(self.speed)
        self.life -= 1
    
    def draw(self, display):
        """draws the paddle.
        display: the pygame instance of the display to draw on."""
        pygame.draw.rect(display, self.color, self.rect)

class PulsatingText:

    Texts = []
    def __init__(self, display, text, center, font_size=36):
        self.display = display
        self.text = text
        self.center = center
        self.font_size = font_size
        self.phase = 0
        PulsatingText.Texts.append(self)

    def update(self):
        self.phase = (self.phase + 0.04) % (2 * math.pi)

    def draw(self):
        pulse_val = abs(math.sin(self.phase)) 
        pulse_color = (pulse_val * 255, pulse_val * 255, pulse_val * 255)
        font = pygame.font.SysFont(None, self.font_size) 
        rendered_text = font.render(self.text, True, pulse_color)
        text_rect = rendered_text.get_rect(center=self.center)
        self.display.blit(rendered_text, text_rect)
            
class Startmenu():
    def __init__(self, display):
        self.selected_gamemode = 'AI'
        self.display = display
        folder_path = "Bilder/Ball"
        self.ball_options = []
        self.index = 0
        self.font_size = 25
        self.font = pygame.font.SysFont(None, self.font_size) 
        for filename in os.listdir(folder_path):
            # Stelle den vollständigen Pfad zur Datei her
            filepath = os.path.join(folder_path, filename)

            # Überprüfe, ob die Datei eine Bilddatei ist (z.B. endet auf .png)
            if filepath.endswith((".png", ".jpg", ".jpeg")):
                # Lade das Bild und füge es zur Liste hinzu
                image = pygame.image.load(filepath)
                image = pygame.transform.scale(image, (radius*4, radius*4)) 
                self.ball_options.append(image)
        
        PulsatingText(display, "Press Spacebar To Play", (screen_size[0]//2, 3*screen_size[1]//4), 36)


    def draw(self):
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



    def next_ball(self):
        # Vorherigen Ball auswählen
        self.index += 1
        if self.index >= len(self.ball_options):
            self.index = 0

    def prev_ball(self):
        # Nächsten Ball auswählen
        self.index -= 1
        if self.index < 0:
            self.index = len(self.ball_options) - 1

    def next_gamemode(self):
        # Vorherigen Gamemode auswählen
        if self.selected_gamemode == 'AI':
            self.selected_gamemode = 'PVP'
        elif self.selected_gamemode == 'PVP':
            self.selected_gamemode = 'AI'

        
    def check_input(self, events):
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
        
    
    def get_curr_im(self):
        image = self.ball_options[self.index]
        image = pygame.transform.scale(image, (radius*2, radius*2)) 
        return image
    
    def get_curr_gamemode(self):
        return self.selected_gamemode




class GameState():
    def __init__(self) -> None:
        self.particles: list = []
        pygame.mixer.init()
        pygame.mixer.music.load("Sounds/music-background.mp3") 
        pygame.mixer.music.play(-1,0.0)

        self.explosion = pygame.mixer.Sound("Sounds/explosion.mp3")
        self.explosion.set_volume(0.2)
        self.bounce = pygame.mixer.Sound("Sounds/bounce.wav")

        # spiel läuft bis zu dieser Punktzahl, anfangs auf 100, damit die Paddles bei Start im Hintergrund lange spielen
        self.game_length = [100]

        self.display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

        self.start_menu = Startmenu(self.display)
        #initialisiert die obstacles
        self.obstacles = [Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), random.randint(50,150), random.randint(50,150)) for i in range(0,2)]
        self.FPS = pygame.time.Clock()
        self.speed_increment = [1]
        self.paddle1 = Paddle(50, screen_size[1]//2 - 175, 15, 150, 12)
        self.paddle2 = Paddle(screen_size[0]-65, screen_size[1]//2 - 175, 15, 150, 12)
        self.ball = Ball(screen_size[0]//2, screen_size[1]//2, radius, 6)
        self.score = [0, 0]
        self.running = True

        self.trace: list = []
        self.MAX_SPEED_SQ = 500
        self.gamemode = ["LAZY"]

        self.do_on_end_bool = True

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

    def draw_winner_text(self, winner_paddle):
        font = pygame.font.SysFont(None, 72, bold=True) 
        text = font.render("Player " + str(self.score.index(max(self.score[0], self.score[1]))+1) + " Wins!", True, (255, 223, 0))
        text_rect = text.get_rect(center=(screen_size[0]//2, screen_size[1]//4))
        pygame.draw.rect(self.display, winner_paddle.color, text_rect, 2)
        self.display.blit(text, text_rect)

    def game_ended_animation(self):
        winner_paddle = self.paddle1 if self.score.index(max(self.score[0],self.score[1])) == 0 else self.paddle2
        x_delta = winner_paddle.rect.centerx - screen_size[0]//2
        y_delta = winner_paddle.rect.centery - screen_size[1]//2
        move_by = [0,0]
        move_speed = 10.0 # adjust this value to change the speed of paddles moving towards center
        if abs(x_delta) > 10:
            move_by[0] = -1.0 * move_speed if x_delta > 0 else move_speed
        if abs(y_delta) > 10:
            move_by[1] = -1.0 * move_speed if y_delta > 0 else move_speed
        winner_paddle.rect.move_ip(move_by)
        winner_paddle.draw(self.display)
        if abs(x_delta) <= 10 and abs(y_delta) <= 10:
            gs.draw_crown((winner_paddle.rect.centerx, winner_paddle.rect.y - 40))
            gs.draw_winner_text(winner_paddle)
        return False

    def move_players(self):
        keys = pygame.key.get_pressed()
        if(self.gamemode[0]=="PVP"):
            self.paddle1.move(keys[pygame.K_w], keys[pygame.K_s])
            self.paddle2.move(keys[pygame.K_UP], keys[pygame.K_DOWN])
        if(self.gamemode[0]=="AI"):
            self.paddle1.move(keys[pygame.K_w], keys[pygame.K_s])
            if(self.ball.speed[0] > 0 and ((self.ball.rect.centery - self.paddle2.rect.centery) > 20 or (self.ball.rect.centery - self.paddle2.rect.centery) < -20)):
                self.paddle2.move(self.ball.rect.centery < self.paddle2.rect.centery, self.ball.rect.centery > self.paddle2.rect.centery)
        if(self.gamemode[0]=="LAZY"):
            if(self.ball.speed[0] > 0 and ((self.ball.rect.centery - self.paddle2.rect.centery) > 20 or (self.ball.rect.centery - self.paddle2.rect.centery) < -20)):
                self.paddle2.move(self.ball.rect.centery < self.paddle2.rect.centery, self.ball.rect.centery > self.paddle2.rect.centery)
            if(self.ball.speed[0] < 0 and ((self.ball.rect.centery - self.paddle1.rect.centery) > 20 or (self.ball.rect.centery - self.paddle1.rect.centery) < -20)):
                self.paddle1.move(self.ball.rect.centery < self.paddle1.rect.centery, self.ball.rect.centery > self.paddle1.rect.centery)

    def check_paddle_colissions(self):
        # Ball kollidiert mit linkem paddle
        if self.ball.rect.colliderect(self.paddle1.rect) and self.ball.speed[0]<0:
            self.ball.speed[0] = -self.ball.speed[0]
            self.ball.speed[1] = random.randint(-10, 10)
            if game_started[0]:
                pygame.mixer.Sound.play(self.bounce)
        # Ball kollidiert mit rechtem paddle
        if self.ball.rect.colliderect(self.paddle2.rect) and self.ball.speed[0]>0:
            self.ball.speed[0] = -self.ball.speed[0]
            self.ball.speed[1] = random.randint(-10, 10) 
            if game_started[0]:
                pygame.mixer.Sound.play(self.bounce)

    def check_ball_scored(self):
        #Punkt für rechts
        if self.ball.rect.left < -10:
            self.score[1] += 1
            self.particles += [Particle(*self.ball.rect.center) for _ in range(300)]
            if game_started[0]:
                pygame.mixer.Sound.play(self.explosion)
            self.ball.rect.center = (screen_size[0]//2, screen_size[1]//2)
            self.ball.speed = [5 * random.choice((-1, 1)), 5 * random.choice((-1, 1))] 
            self.ball.speed = [5 * random.choice((-1.5, 1.5)), 5 * random.choice((-1, 1))] 
            self.speed_increment[0] = 1
            self.obstacles.pop(0)
            self.obstacles.append(Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), random.randint(50,150), random.randint(50,150)))

        #Punkt für links
        elif self.ball.rect.right > screen_size[0]+10:
            self.score[0] += 1
            self.particles += [Particle(*self.ball.rect.center) for _ in range(300)]
            if game_started[0]:
                pygame.mixer.Sound.play(self.explosion)
            self.ball.rect.center = (screen_size[0]//2, screen_size[1]//2)
            self.ball.speed = [5 * random.choice((-1, 1)), 5 * random.choice((-1, 1))] 
            self.ball.speed = [5 * random.choice((-1.5, 1.5)), 5 * random.choice((-1, 1))] 
            self.speed_increment[0] = 1
            self.obstacles.pop(1)
            self.obstacles.append(Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), random.randint(50,150), random.randint(50,150)))

    def check_colissions_obstacles(self):
        #hindernisse zeichnen und kollision
        for obstacle in self.obstacles:  
            if self.ball.rect.colliderect(obstacle.rect):
                obstacle.collide_with(self.ball)
                if game_started[0]:
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
        total_speed = self.ball.speed[0]*self.ball.speed[0]*self.speed_increment[0] + self.ball.speed[1]*self.ball.speed[1]*self.speed_increment[0]
        # Überprüfen, ob die Gesamtgeschwindigkeit den maximalen Wert überschritten hat
        if total_speed < self.MAX_SPEED_SQ:
            self.speed_increment[0] = self.speed_increment[0] + 0.0002

    def game_ended(self):
        gs.game_ended_animation()

    def reset_game(self):
        self.gamemode[0] = self.start_menu.get_curr_gamemode()
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
        game_started[0] = True
        self.game_length[0] = 5
        self.ball.rect.center = (screen_size[0]//2, screen_size[1]//2)
        self.ball.speed = [5 * random.choice((-1, 1)), 5 * random.choice((-1, 1))] 
        self.ball.speed = [5 * random.choice((-1.5, 1.5)), 5 * random.choice((-1, 1))] 
        self.speed_increment[0] = 1
        self.display.fill((15,15,15))
        gs.show_score()
        gs.draw_obstacles()
        self.paddle1.draw(self.display)
        self.paddle2.draw(self.display)
        self.ball.image = self.start_menu.get_curr_im()
        self.ball.draw(self.display)
        self.trace.clear()
        pygame.mouse.set_visible(False)
        pygame.display.update()
        pygame.event.pump()
        pygame.time.delay(1500)  
   
gs = GameState()

# main game loop
while gs.running:
    if max(gs.score[0], gs.score[1]) < gs.game_length[0]:
        gs.trace += [Trace_particle(*gs.ball.rect.center)]
    try:
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
                    if not game_started[0]:
                        gs.reset_game()
                        gs.gamemode[0] = gs.start_menu.get_curr_gamemode()
                    if event.key == pygame.K_SPACE and max(gs.score[0], gs.score[1]) >= gs.game_length[0]:
                        gs.reset_game()
                        gs.do_on_end_bool = True


        if max(gs.score[0], gs.score[1]) < gs.game_length[0]:
            gs.move_players()
            gs.check_paddle_colissions()
            gs.check_colissions_obstacles()
            gs.ball.move(gs.speed_increment[0])
            gs.increase_speed()
            gs.check_ball_scored()
        #bild reseten (entspricht Hintergrundfarbe)
        gs.display.fill((15, 15, 15))
        gs.update_draw_particles()
        gs.show_score()
        gs.draw_obstacles()

        if max(gs.score[0], gs.score[1]) >= gs.game_length[0]:
            gs.dim_screen(60)

        #paddles und ball zeichnen
        gs.paddle1.draw(gs.display)
        gs.paddle2.draw(gs.display)
        if max(gs.score[0], gs.score[1]) < gs.game_length[0]:
            gs.ball.draw(gs.display)
        if max(gs.score[0], gs.score[1]) >= gs.game_length[0]:
            gs.game_ended()
            if gs.do_on_end_bool:
                PulsatingText(gs.display, "Press Spacebar To Continue", (screen_size[0]//2, 3*screen_size[1]//4), 36)
                gs.do_on_end_bool = False

        
        if not game_started[0]:
            gs.dim_screen(70)
            gs.start_menu.check_input(events)
            gs.start_menu.draw()

        for t in PulsatingText.Texts:
            t.update()
            t.draw()
            
        pygame.display.flip()
        gs.FPS.tick(60) #limitiert bildwiederholungsrate auf 60 fps
   
    except Exception as e:
        
        print('Fehler : ',e, '  Fehler in Zeile: ', e.__traceback__.tb_lineno)
        gs.running = False
        break
pygame.quit()
sys.exit()