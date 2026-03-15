import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from collections import defaultdict

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Courier', 16)
display = (1200, 800)
screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("Minecraft Python")
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# Set up perspective with 90 degree FOV
glMatrixMode(GL_PROJECTION)
gluPerspective(90, (display[0] / display[1]), 0.1, 500.0)
glMatrixMode(GL_MODELVIEW)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)
glCullFace(GL_BACK)
glClearColor(0.5, 0.7, 1.0, 1.0)  # Sky blue background

# Set up lighting with proper material properties
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

# Material properties
glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 0)
glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
glMaterial(GL_FRONT_AND_BACK, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])

# Light properties
light_pos = [50, 100, 50, 0]
light_ambient = [0.4, 0.4, 0.4, 1.0]
light_diffuse = [0.8, 0.8, 0.8, 1.0]
glLight(GL_LIGHT0, GL_POSITION, light_pos)
glLight(GL_LIGHT0, GL_AMBIENT, light_ambient)
glLight(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

# World storage
blocks = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

# Create island terrain with layers
import math as math_module
np.random.seed(42)

center_x, center_z = 0, 0
island_radius = 20

# Create layered island with sand and dirt
for x in range(-25, 25):
    for z in range(-25, 25):
        distance = math_module.sqrt((x - center_x) ** 2 + (z - center_z) ** 2)
        
        if distance < island_radius:
            # Base stone layer (y=0-1)
            blocks[x][0][z] = 3  # Stone blocks
            
            # Height-based terrain
            max_height = int(6 - (distance / island_radius) * 5)
            
            # Add hill in center
            hill_distance = math_module.sqrt((x - center_x) ** 2 + (z - center_z) ** 2)
            if hill_distance < 8:
                max_height += 3 + int(3 * (1 - hill_distance / 8))
            
            height = max(1, max_height)
            
            # Add variation
            height += np.random.randint(-1, 2)
            height = max(1, min(12, height))
            
            # Fill layers
            for y in range(height):
                if y == 0:
                    blocks[x][y][z] = 3  # Stone
                elif y < height - 1:
                    blocks[x][y][z] = 2  # Dirt
                else:
                    blocks[x][y][z] = 1  # Grass on top
        
        # Sand beach around island
        elif distance < island_radius + 3:
            blocks[x][0][z] = 4  # Sand

# Add a tree on the hill
tree_x, tree_z = 2, 2
tree_base_y = 10

# Tree trunk (wood)
for y in range(tree_base_y, tree_base_y + 5):
    blocks[tree_x][y][tree_z] = 5  # Wood

# Tree foliage (leaves) - sphere shape
foliage_radius = 3
foliage_y = tree_base_y + 4
for dx in range(-foliage_radius, foliage_radius + 1):
    for dy in range(-foliage_radius, foliage_radius + 1):
        for dz in range(-foliage_radius, foliage_radius + 1):
            dist = math_module.sqrt(dx**2 + dy**2 + dz**2)
            if dist < foliage_radius and (dx != 0 or dz != 0 or dy > -2):
                blocks[tree_x + dx][foliage_y + dy][tree_z + dz] = 6  # Leaves

# Camera
camera_pos = [0, 20, 0]  # Start higher to avoid collision issues
camera_rot = [-30, 0]  # Look down slightly
velocity_y = 0  # For gravity
on_ground = False
space_pressed_last = False  # Track if space was pressed last frame

# Block type to color mapping
block_colors = {
    1: (0.35, 0.95, 0.35),  # Grass - bright green
    2: (0.6, 0.45, 0.25),   # Dirt - brown
    3: (0.5, 0.5, 0.5),     # Stone - gray
    4: (0.95, 0.85, 0.5),   # Sand - yellow
    5: (0.7, 0.5, 0.3),     # Wood - brown
    6: (0.2, 0.7, 0.2),     # Leaves - dark green
}

# Hotbar colors (different block types for quick selection)
hotbar_colors = [
    (0.35, 0.95, 0.35),  # Grass
    (0.6, 0.45, 0.25),   # Dirt
    (0.5, 0.5, 0.5),     # Stone
    (0.95, 0.85, 0.5),   # Sand
    (0.7, 0.5, 0.3),     # Wood
    (0.2, 0.7, 0.2),     # Leaves
    (1.0, 0.0, 0.0),     # Red
    (0.0, 1.0, 0.0),     # Green
    (0.0, 0.0, 1.0),     # Blue
    (1.0, 1.0, 0.0),     # Yellow
]

current_block = 1  # Currently selected block type
break_cooldown = 0  # Cooldown timer for breaking blocks

def draw_cube(x, y, z, block_type=1):
    """Draw a cube with color based on block type"""
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Get color for this block type
    color = block_colors.get(block_type, (0.5, 0.5, 0.5))
    
    # Slightly darker/lighter variants for different faces
    colors = {
        'front': (color[0] * 1.0, color[1] * 1.0, color[2] * 1.0),
        'back': (color[0] * 0.9, color[1] * 0.9, color[2] * 0.9),
        'top': (color[0] * 1.1, color[1] * 1.1, color[2] * 1.1),
        'bottom': (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7),
        'left': (color[0] * 0.85, color[1] * 0.85, color[2] * 0.85),
        'right': (color[0] * 0.95, color[1] * 0.95, color[2] * 0.95),
    }
    
    # Check which faces are visible
    faces_to_draw = []
    
    # Front face (z+)
    if not check_collision(x, y, z + 1):
        faces_to_draw.append({
            'normal': (0, 0, 1),
            'vertices': [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
            'color': colors['front']
        })
    
    # Back face (z-)
    if not check_collision(x, y, z - 1):
        faces_to_draw.append({
            'normal': (0, 0, -1),
            'vertices': [(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)],
            'color': colors['back']
        })
    
    # Top face (y+)
    if not check_collision(x, y + 1, z):
        faces_to_draw.append({
            'normal': (0, 1, 0),
            'vertices': [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)],
            'color': colors['top']
        })
    
    # Bottom face (y-)
    if not check_collision(x, y - 1, z):
        faces_to_draw.append({
            'normal': (0, -1, 0),
            'vertices': [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
            'color': colors['bottom']
        })
    
    # Left face (x-)
    if not check_collision(x - 1, y, z):
        faces_to_draw.append({
            'normal': (-1, 0, 0),
            'vertices': [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],
            'color': colors['left']
        })
    
    # Right face (x+)
    if not check_collision(x + 1, y, z):
        faces_to_draw.append({
            'normal': (1, 0, 0),
            'vertices': [(1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)],
            'color': colors['right']
        })
    
    # Only render if there are visible faces
    if faces_to_draw:
        glBegin(GL_QUADS)
        for face in faces_to_draw:
            glNormal3fv(face['normal'])
            glColor3fv(face['color'])
            for vertex in face['vertices']:
                glVertex3fv(vertex)
        glEnd()
    
    glPopMatrix()

def update_camera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(camera_rot[0], 1, 0, 0)
    glRotatef(camera_rot[1], 0, 1, 0)
    glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])

def raycast(max_dist=100):
    sin_pitch = math.sin(math.radians(camera_rot[0]))
    cos_pitch = math.cos(math.radians(camera_rot[0]))
    sin_yaw = math.sin(math.radians(camera_rot[1]))
    cos_yaw = math.cos(math.radians(camera_rot[1]))
    
    dx = sin_yaw * cos_pitch
    dy = -sin_pitch
    dz = -cos_yaw * cos_pitch
    
    for dist in range(1, max_dist):
        x = int(camera_pos[0] + dx * dist)
        y = int(camera_pos[1] + dy * dist)
        z = int(camera_pos[2] + dz * dist)
        if blocks[x][y][z]:
            return (x, y, z)
    return None

def check_collision(x, y, z):
    """Check if position collides with a block"""
    return blocks[int(x)][int(y)][int(z)] != 0

def is_player_colliding():
    """Check if player bounding box collides with blocks using AABB"""
    player_height = 1.8
    player_width = 0.6
    
    # Player bounding box
    min_x = camera_pos[0] - player_width / 2
    max_x = camera_pos[0] + player_width / 2
    min_y = camera_pos[1] - player_height
    max_y = camera_pos[1]
    min_z = camera_pos[2] - player_width / 2
    max_z = camera_pos[2] + player_width / 2
    
    # Check blocks that could intersect
    for x in range(int(min_x) - 1, int(max_x) + 2):
        for y in range(int(min_y) - 1, int(max_y) + 2):
            for z in range(int(min_z) - 1, int(max_z) + 2):
                if blocks[x][y][z]:
                    # Block exists, check AABB collision
                    block_min_x, block_max_x = x, x + 1
                    block_min_y, block_max_y = y, y + 1
                    block_min_z, block_max_z = z, z + 1
                    
                    # AABB collision test
                    if (min_x < block_max_x and max_x > block_min_x and
                        min_y < block_max_y and max_y > block_min_y and
                        min_z < block_max_z and max_z > block_min_z):
                        return True
    return False

def get_ground_level():
    """Find the Y position of the ground beneath the player"""
    player_height = 1.8
    player_width = 0.6
    
    min_x = camera_pos[0] - player_width / 2
    max_x = camera_pos[0] + player_width / 2
    min_z = camera_pos[2] - player_width / 2
    max_z = camera_pos[2] + player_width / 2
    
    # Search from player position downward for blocks
    for y in range(int(camera_pos[1]), -1, -1):
        for x in range(int(min_x) - 1, int(max_x) + 2):
            for z in range(int(min_z) - 1, int(max_z) + 2):
                if blocks[x][y][z]:
                    return y + 1 + player_height
    
    return 1 + player_height

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    keys = pygame.key.get_pressed()
    
    # Movement
    if keys[pygame.K_w]:
        camera_pos[0] += math.sin(math.radians(camera_rot[1])) * 0.1
        camera_pos[2] -= math.cos(math.radians(camera_rot[1])) * 0.1
    if keys[pygame.K_s]:
        camera_pos[0] -= math.sin(math.radians(camera_rot[1])) * 0.1
        camera_pos[2] += math.cos(math.radians(camera_rot[1])) * 0.1
    if keys[pygame.K_a]:
        camera_pos[0] -= math.cos(math.radians(camera_rot[1])) * 0.1
        camera_pos[2] -= math.sin(math.radians(camera_rot[1])) * 0.1
    if keys[pygame.K_d]:
        camera_pos[0] += math.cos(math.radians(camera_rot[1])) * 0.1
        camera_pos[2] += math.sin(math.radians(camera_rot[1])) * 0.1
    if keys[pygame.K_SPACE]:
        camera_pos[1] += 0.2
    if keys[pygame.K_LCTRL]:
        camera_pos[1] -= 0.2
    
    # Apply gravity
    velocity_y -= 0.02  # Gravity acceleration
    new_y = camera_pos[1] + velocity_y
    camera_pos[1] = new_y
    
    # Check collision and resolve
    if is_player_colliding():
        # Move player up to ground level
        ground_y = get_ground_level()
        camera_pos[1] = ground_y
        velocity_y = 0
        on_ground = True
    else:
        on_ground = False
    
    # Jump with space (only when on ground, and only on rising edge)
    space_pressed = keys[pygame.K_SPACE]
    if space_pressed and not space_pressed_last and on_ground:
        velocity_y = 0.5  # Jump impulse
    space_pressed_last = space_pressed
    
    # Mouse look (always active)
    mouse_rel = pygame.mouse.get_rel()
    camera_rot[1] += mouse_rel[0] * 0.2
    camera_rot[0] += mouse_rel[1] * 0.2  # Fixed: was -= now +=
    camera_rot[0] = max(-90, min(90, camera_rot[0]))  # Clamp pitch
    
    # Block destruction (left click)
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0] and break_cooldown <= 0:  # Left click to destroy
        block = raycast()
        if block:
            blocks[block[0]][block[1]][block[2]] = 0
            break_cooldown = 0.2  # 200ms cooldown
    
    # Decrease break cooldown
    break_cooldown -= clock.get_time() / 1000.0
    
    # Block placement (right click)
    if mouse_buttons[2]:  # Right click to place
        block = raycast()
        if block:
            # Place block adjacent to the one we're looking at
            blocks[block[0]][block[1]+1][block[2]] = current_block
    
    # Hotbar selection (number keys 1-0)
    if keys[pygame.K_1]:
        current_block = 1
    elif keys[pygame.K_2]:
        current_block = 2
    elif keys[pygame.K_3]:
        current_block = 3
    elif keys[pygame.K_4]:
        current_block = 4
    elif keys[pygame.K_5]:
        current_block = 5
    elif keys[pygame.K_6]:
        current_block = 6
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    update_camera()
    
    # Draw visible blocks with optimized render distance
    render_distance = 10  # Reduced from 12
    blocks_drawn = 0
    for x in range(int(camera_pos[0])-render_distance, int(camera_pos[0])+render_distance):
        for z in range(int(camera_pos[2])-render_distance, int(camera_pos[2])+render_distance):
            for y in range(max(0, int(camera_pos[1])-render_distance), min(int(camera_pos[1])+render_distance, 50)):
                block_type = blocks[x][y][z]
                if block_type:
                    draw_cube(x, y, z, block_type)
                    blocks_drawn += 1
    
    # Draw 2D HUD (crosshair and hotbar)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, display[0], display[1], 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # Draw crosshair
    crosshair_size = 10
    center_x, center_y = display[0] / 2, display[1] / 2
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    glVertex2f(center_x - crosshair_size, center_y)
    glVertex2f(center_x + crosshair_size, center_y)
    glVertex2f(center_x, center_y - crosshair_size)
    glVertex2f(center_x, center_y + crosshair_size)
    glEnd()
    
    # Draw hotbar
    hotbar_y = display[1] - 50
    hotbar_x_start = display[0] / 2 - (10 * 35) / 2
    slot_size = 35
    slot_spacing = 2
    
    for i in range(10):
        x = hotbar_x_start + i * (slot_size + slot_spacing)
        y = hotbar_y
        
        # Draw slot background
        if i == current_block - 1:
            glColor3f(1, 1, 0)  # Yellow border for selected
        else:
            glColor3f(0.5, 0.5, 0.5)
        
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + slot_size, y)
        glVertex2f(x + slot_size, y + slot_size)
        glVertex2f(x, y + slot_size)
        glEnd()
        
        # Draw colored block in slot
        color = hotbar_colors[i]
        glColor3fv(color)
        glBegin(GL_QUADS)
        glVertex2f(x + 3, y + 3)
        glVertex2f(x + slot_size - 3, y + 3)
        glVertex2f(x + slot_size - 3, y + slot_size - 3)
        glVertex2f(x + 3, y + slot_size - 3)
        glEnd()
    
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()