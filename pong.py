import pygame
import sys
import random
import math

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
        self.color = (255, 255, 255)
        self.speed = [speed * random.choice((-1, 1)), speed * random.choice((-1, 1))]

    def draw(self, display:pygame.display):
        """draws the ball onto the frame.
        
        display: instance of the display the ball should be drawn too."""
        pygame.draw.ellipse(display, self.color, self.rect)

    def move(self, speed_inc):
        """function to move the ball, including colission with playfield-boundries."""
        
        if self.rect.top < 0:
            if self.speed[1] < 0:
                self.speed[1] = -self.speed[1]
            
        if self.rect.bottom > screen_size[1]:
            if self.speed[1] > 0:
                self.speed[1] = -self.speed[1]
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


pygame.init()



info_object = pygame.display.Info()
screen_size = (info_object.current_w, info_object.current_h)
display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

obstacles = [Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), 50, 50) for _ in range(4)]

FPS = pygame.time.Clock()

speed_increment = [1]

paddle1 = Paddle(50, screen_size[1]//2 - 175, 15, 150, 12)
paddle2 = Paddle(screen_size[0]-65, screen_size[1]//2 - 175, 15, 150, 12)
ball = Ball(screen_size[0]//2, screen_size[1]//2, 30, 6)

score = [0, 0]

running = True
particles = []
trace = []
MAX_SPEED_SQ = 500
gamemode = "AI"

def move_players():
    keys = pygame.key.get_pressed()

    if(gamemode=="PVP"):
        paddle1.move(keys[pygame.K_w], keys[pygame.K_s])
        paddle2.move(keys[pygame.K_UP], keys[pygame.K_DOWN])
    if(gamemode=="AI"):
        paddle1.move(keys[pygame.K_w], keys[pygame.K_s])
        if(ball.speed[0] > 0 and ((ball.rect.centery - paddle2.rect.centery) > 20 or (ball.rect.centery - paddle2.rect.centery) < -20)):
            paddle2.move(ball.rect.centery < paddle2.rect.centery, ball.rect.centery > paddle2.rect.centery)
    if(gamemode=="LAZY"):
        if(ball.speed[0] > 0 and ((ball.rect.centery - paddle2.rect.centery) > 20 or (ball.rect.centery - paddle2.rect.centery) < -20)):
            paddle2.move(ball.rect.centery < paddle2.rect.centery, ball.rect.centery > paddle2.rect.centery)
        if(ball.speed[0] < 0 and ((ball.rect.centery - paddle1.rect.centery) > 20 or (ball.rect.centery - paddle1.rect.centery) < -20)):
            paddle1.move(ball.rect.centery < paddle1.rect.centery, ball.rect.centery > paddle1.rect.centery)


def check_paddle_colissions():
     # Ball kollidiert mit linkem paddle
        if ball.rect.colliderect(paddle1.rect) and ball.speed[0]<0:
            ball.speed[0] = -ball.speed[0]
            ball.speed[1] = random.randint(-10, 10)

        # Ball kollidiert mit rechtem paddle
        if ball.rect.colliderect(paddle2.rect) and ball.speed[0]>0:
            ball.speed[0] = -ball.speed[0]
            ball.speed[1] = random.randint(-10, 10) 


def check_ball_scored(particles):
        #Punkt für rechts
        if ball.rect.left < -10:
            score[1] += 1
            particles += [Particle(*ball.rect.center) for _ in range(300)]
            ball.rect.center = (screen_size[0]//2, screen_size[1]//2)
            ball.speed = [5 * random.choice((-1, 1)), 5 * random.choice((-1, 1))] 
            speed_increment[0] = 1
            obstacles.append(Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), 50, 50))

        #Punkt für links
        elif ball.rect.right > screen_size[0]+10:
            score[0] += 1
            particles += [Particle(*ball.rect.center) for _ in range(300)]
            ball.rect.center = (screen_size[0]//2, screen_size[1]//2)
            ball.speed = [5 * random.choice((-1, 1)), 5 * random.choice((-1, 1))] 
            speed_increment[0] = 1
            obstacles.append(Obstacle(random.randint(100, screen_size[0]-100), random.randint(100, screen_size[1]-100), 50, 50))


def check_colissions_obstacles():
    #hindernisse zeichnen und kollision
    for obstacle in obstacles:  
        if ball.rect.colliderect(obstacle.rect):
            obstacle.collide_with(ball)

def draw_obstacles():
    for obstacle in obstacles:  
            obstacle.draw(display)

def update_draw_particles():
    # update and draw the particles
        for particle in particles:
            particle.update()
            particle.draw(display)
            if particle.life <= 0:
                particles.remove(particle)

        #trace zeichnen und updaten
        for particle in trace:
            particle.update()
            particle.draw(display)
            if particle.life <= 0:
                trace.remove(particle)

def zeige_spielstand():
    font = pygame.font.Font(None, 46)
    text = font.render("" + str(score[0]) + " : " + str(score[1]), 1, (255, 255, 255))
    display.blit(text, (screen_size[0]//2 -30, 40))
     
def increase_speed():
    # Quadratisches summe der Geschwindigkeiten
    total_speed = ball.speed[0]*ball.speed[0]*speed_increment[0] + ball.speed[1]*ball.speed[1]*speed_increment[0]

    # Überprüfen, ob die Gesamtgeschwindigkeit den maximalen Wert überschritten hat
    if total_speed < MAX_SPEED_SQ:
        speed_increment[0] = speed_increment[0] + 0.0002





# main game loop
while running:
    trace += [Trace_particle(*ball.rect.center)]
    try:
        #checkt ob das Spiel beendet wurde
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False



        move_players()
        check_paddle_colissions()
        check_colissions_obstacles()
        ball.move(speed_increment[0])
        increase_speed()
        check_ball_scored(particles)

        #bild reseten (entspricht Hintergrundfarbe)
        display.fill((0, 0, 0))

        update_draw_particles()
        zeige_spielstand()
        draw_obstacles()

        #paddles und ball zeichnen
        paddle1.draw(display)
        paddle2.draw(display)
        ball.draw(display)

        pygame.display.flip()

        FPS.tick(60) #limitiert bildwiederholungsrate auf 60 fps
   
    except Exception as e:
        
        print('Fehler : ',e, '  Fehler in Zeile: ', e.__traceback__.tb_lineno)
        running = False
        break


pygame.quit()
sys.exit()