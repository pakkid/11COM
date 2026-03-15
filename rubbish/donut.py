import math
import sys

import pygame


WIDTH, HEIGHT = 800, 600
FOV = 600
R1 = 90
R2 = 40
SAMPLES_THETA = 96
SAMPLES_PHI = 72
SUPERSAMPLE = 1
TARGET_FPS = 50


def hsv_to_rgb(h, s, v):
    h = h % 1.0
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    i = i % 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)


def rotate_x(y, z, angle):
    ca = math.cos(angle)
    sa = math.sin(angle)
    return y * ca - z * sa, y * sa + z * ca


def rotate_y(x, z, angle):
    ca = math.cos(angle)
    sa = math.sin(angle)
    return x * ca + z * sa, -x * sa + z * ca


def rotate_z(x, y, angle):
    ca = math.cos(angle)
    sa = math.sin(angle)
    return x * ca - y * sa, x * sa + y * ca


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spinning RGB Donut")
    clock = pygame.time.Clock()

    render_w = WIDTH * SUPERSAMPLE
    render_h = HEIGHT * SUPERSAMPLE
    render_surface = pygame.Surface((render_w, render_h))

    a = 0.0
    b = 0.0

    theta_step = 2 * math.pi / SAMPLES_THETA
    phi_step = 2 * math.pi / SAMPLES_PHI

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        render_surface.fill((0, 0, 0))

        quads = []

        for i in range(SAMPLES_THETA):
            theta = i * theta_step
            theta2 = (i + 1) * theta_step
            ct = math.cos(theta)
            st = math.sin(theta)
            ct2 = math.cos(theta2)
            st2 = math.sin(theta2)

            for j in range(SAMPLES_PHI):
                phi = j * phi_step
                phi2 = (j + 1) * phi_step
                cp = math.cos(phi)
                sp = math.sin(phi)
                cp2 = math.cos(phi2)
                sp2 = math.sin(phi2)

                def torus_point(cos_t, sin_t, cos_p, sin_p):
                    circle_x = R1 + R2 * cos_p
                    circle_y = R2 * sin_p
                    x = circle_x * cos_t
                    y = circle_x * sin_t
                    z = circle_y
                    y, z = rotate_x(y, z, a)
                    x, z = rotate_y(x, z, b)
                    x, y = rotate_z(x, y, a * 0.5)
                    z += 300
                    return x, y, z

                p1 = torus_point(ct, st, cp, sp)
                p2 = torus_point(ct2, st2, cp, sp)
                p3 = torus_point(ct2, st2, cp2, sp2)
                p4 = torus_point(ct, st, cp2, sp2)

                if min(p1[2], p2[2], p3[2], p4[2]) <= 0:
                    continue

                def project(p):
                    ooz = FOV / p[2]
                    return (
                        render_w / 2 + p[0] * ooz * SUPERSAMPLE,
                        render_h / 2 - p[1] * ooz * SUPERSAMPLE,
                    )

                v1 = project(p1)
                v2 = project(p2)
                v3 = project(p3)
                v4 = project(p4)

                nx = cp * ct
                ny = cp * st
                nz = sp
                ny, nz = rotate_x(ny, nz, a)
                nx, nz = rotate_y(nx, nz, b)
                nx, ny = rotate_z(nx, ny, a * 0.5)

                light = (nx * 0.2 + ny * 0.6 + nz * 0.8)
                light = max(0.0, min(1.0, (light + 1) / 2))

                hue = (theta / (2 * math.pi) + b * 0.05) % 1.0
                color = hsv_to_rgb(hue, 1.0, 0.2 + 0.8 * light)

                depth = (p1[2] + p2[2] + p3[2] + p4[2]) / 4.0
                quads.append((depth, color, [v1, v2, v3, v4]))

        quads.sort(key=lambda q: q[0], reverse=True)
        for _, color, verts in quads:
            pygame.draw.polygon(render_surface, color, verts)

        if SUPERSAMPLE > 1:
            frame = pygame.transform.smoothscale(render_surface, (WIDTH, HEIGHT))
        else:
            frame = render_surface
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        a += 0.015
        b += 0.01
        clock.tick(TARGET_FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()