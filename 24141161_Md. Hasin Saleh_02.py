# Catch the Diamonds

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import time
import random

#Global Variables -
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

STATE_PLAYING = 0
STATE_PAUSED = 1
STATE_GAMEOVER = 2

gameState = STATE_PLAYING
score = 0
previous_time = 0

diamond_radius = 20
diamond_speed_initial = 100.0
diamond_speed = diamond_speed_initial
diamond_acceleration = 10.0
diamond_x = 0
diamond_y = WINDOW_HEIGHT - diamond_radius
diamond_color = (1.0, 1.0, 1.0)

catcher_y = 50
catcher_width = 100
catcher_height = 20
catcher_x = WINDOW_WIDTH // 2
catcher_color_normal = (1.0, 1.0, 1.0)
catcher_color_gameover = (1.0, 0.0, 0.0)

button_size = 60
left_button = {'x': 50, 'y': WINDOW_HEIGHT - 50, 'size': button_size}
middle_button = {'x': WINDOW_WIDTH // 2, 'y': WINDOW_HEIGHT - 50, 'size': button_size}
right_button = {'x': WINDOW_WIDTH - 50, 'y': WINDOW_HEIGHT - 50, 'size': button_size}

#Midpoint Line Drawing Algorithm - Eight way symmetry
def draw_line(x1, y1, x2, y2):
    x1 = int(round(x1))
    y1 = int(round(y1))
    x2 = int(round(x2))
    y2 = int(round(y2))

    dx = x2 - x1
    dy = y2 - y1

    x, y = x1, y1

    steep = abs(dy) > abs(dx)
    if steep:
        x, y = y, x
        dx, dy = dy, dx
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dx = x2 - x1
    dy = y2 - y1

    d = 2 * abs(dy) - abs(dx)
    incrE = 2 * abs(dy)
    incrNE = 2 * (abs(dy) - abs(dx))

    x = x1
    y = y1

    glBegin(GL_POINTS)
    if steep:
        glVertex2i(y, x)
    else:
        glVertex2i(x, y)

    while x < x2:
        if d <= 0:
            d += incrE
        else:
            d += incrNE
            if (dy > 0 and not steep) or (dy < 0 and steep):
                y += 1
            else:
                y -= 1
        x += 1
        if steep:
            glVertex2i(y, x)
        else:
            glVertex2i(x, y)
    glEnd()

#Shape Drawing Functions -
def draw_polygon(points):
    num_points = len(points)
    for i in range(num_points):
        x1, y1 = points[i]
        x2, y2 = points[(i+1) % num_points]
        draw_line(x1, y1, x2, y2)

def draw_diamond(cx, cy, r):
    vertices = [(cx, cy + r),
                (cx + r, cy),
                (cx, cy - r),
                (cx - r, cy)]
    draw_polygon(vertices)

def draw_catcher(cx, base_y, width, height, color):
    glColor3f(*color)

    vertices = [
        (cx - width/4, base_y - height/2),  # Bottom left
        (cx - width/2, base_y + height/2),  # Top left
        (cx + width/2, base_y + height/2),  # Top right
        (cx + width/4, base_y - height/2)   # Bottom right
    ]
    draw_polygon(vertices)

def draw_left_button():
    glColor3f(0.0, 0.8, 0.8)
    x = left_button['x']
    y = left_button['y']
    size = left_button['size']
    vertices = [(x - size/4, y),
                (x + size/4, y + size/4),
                (x + size/4, y - size/4)]
    draw_polygon(vertices)

def draw_middle_button():
    glColor3f(1.0, 0.75, 0.0)
    x = middle_button['x']
    y = middle_button['y']
    size = middle_button['size']
    
    if gameState == STATE_PAUSED:
        vertices = [(x - size/8, y - size/4),
                    (x - size/8, y + size/4),
                    (x + size/4, y)]
        draw_polygon(vertices)
    elif gameState == STATE_PLAYING:
        left_bar = [(x - size/4, y - size/4),
                    (x - size/4, y + size/4),
                    (x - size/8, y + size/4),
                    (x - size/8, y - size/4)]
        right_bar = [(x + size/8, y - size/4),
                     (x + size/8, y + size/4),
                     (x + size/4, y + size/4),
                     (x + size/4, y - size/4)]
        draw_polygon(left_bar)
        draw_polygon(right_bar)
    else:
        vertices = [(x - size/8, y - size/4),
                    (x - size/8, y + size/4),
                    (x + size/4, y)]
        draw_polygon(vertices)

def draw_right_button():
    glColor3f(1.0, 0.0, 0.0)
    x = right_button['x']
    y = right_button['y']
    size = right_button['size']
    draw_line(x - size/4, y + size/4, x + size/4, y - size/4)
    draw_line(x - size/4, y - size/4, x + size/4, y + size/4)

#Collision Detection (AABB collision)- 
def check_collision():
    d_left   = diamond_x - diamond_radius
    d_right  = diamond_x + diamond_radius
    d_top    = diamond_y + diamond_radius
    d_bottom = diamond_y - diamond_radius

    catcher_left   = catcher_x - catcher_width/2
    catcher_right  = catcher_x + catcher_width/2
    catcher_bottom = catcher_y
    catcher_top    = catcher_y + catcher_height

    return (d_left < catcher_right and
            d_right > catcher_left and
            d_bottom < catcher_top and
            d_top > catcher_bottom)

#Game Logic -
def spawn_new_diamond():
    global diamond_x, diamond_y, diamond_color, diamond_speed
    diamond_x = random.randint(diamond_radius, WINDOW_WIDTH - diamond_radius)
    diamond_y = WINDOW_HEIGHT - diamond_radius
    diamond_color = (random.uniform(0.5, 1.0),
                     random.uniform(0.5, 1.0),
                     random.uniform(0.5, 1.0))
    diamond_speed = diamond_speed_initial

def reset_game():
    global score, gameState, catcher_x
    score = 0
    gameState = STATE_PLAYING
    catcher_x = WINDOW_WIDTH // 2
    spawn_new_diamond()
    print("Starting Over")

#Callbacks -
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    if gameState != STATE_GAMEOVER:
        glColor3f(*diamond_color)
        draw_diamond(diamond_x, diamond_y, diamond_radius)
    
    if gameState == STATE_GAMEOVER:
        cur_catcher_color = catcher_color_gameover
    else:
        cur_catcher_color = catcher_color_normal
    draw_catcher(catcher_x, catcher_y, catcher_width, catcher_height, cur_catcher_color)
    
    draw_left_button()
    draw_middle_button()
    draw_right_button()
    
    glutSwapBuffers()

def update(): #delta-timing
    global diamond_y, diamond_speed, score, gameState, previous_time
    current_time = time.time()
    if previous_time == 0:
        previous_time = current_time
    dt = current_time - previous_time
    previous_time = current_time

    if gameState == STATE_PLAYING:
        diamond_y -= diamond_speed * dt
        diamond_speed += diamond_acceleration * dt

        if check_collision():
            score += 1
            print("Score:", score)
            spawn_new_diamond()
        elif diamond_y < 0:
            gameState = STATE_GAMEOVER
            print("Game Over. Final Score:", score)
    
    glutPostRedisplay()

def special_keys(key, x, y):
    global catcher_x
    step = 20
    if gameState != STATE_PLAYING:
        return
    if key == GLUT_KEY_LEFT:
        catcher_x -= step
        if catcher_x - catcher_width/2 < 0:
            catcher_x = catcher_width/2
    elif key == GLUT_KEY_RIGHT:
        catcher_x += step
        if catcher_x + catcher_width/2 > WINDOW_WIDTH:
            catcher_x = WINDOW_WIDTH - catcher_width/2

def mouse_click(button, state, x, y):
    global gameState
    if state != GLUT_DOWN:
        return

    y = WINDOW_HEIGHT - y

    if (abs(x - left_button['x']) < left_button['size']/2 and 
        abs(y - left_button['y']) < left_button['size']/2):
        reset_game()
        return

    if (abs(x - middle_button['x']) < middle_button['size']/2 and 
        abs(y - middle_button['y']) < middle_button['size']/2):
        if gameState == STATE_PLAYING:
            gameState = STATE_PAUSED
        elif gameState == STATE_PAUSED:
            gameState = STATE_PLAYING
        return

    if (abs(x - right_button['x']) < right_button['size']/2 and 
        abs(y - right_button['y']) < right_button['size']/2):
        print("Goodbye. Final Score:", score)
        glutLeaveMainLoop()
        return

def reshape(width, height):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH = width
    WINDOW_HEIGHT = height
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(2.0)
    spawn_new_diamond()


def main():
    global previous_time
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Catch the Diamonds!")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(update)
    glutReshapeFunc(reshape)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse_click)
    previous_time = time.time()
    glutMainLoop()

if __name__ == '__main__':
    main()
