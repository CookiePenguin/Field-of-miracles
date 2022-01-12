import os
import sys
import pygame

pygame.init()
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Окно')
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


img_baraban = load_image('барабан.png')
baraban = pygame.sprite.Sprite()
baraban.image = pygame.transform.scale(img_baraban, (600, 600))
baraban.rect = baraban.image.get_rect()
baraban.rect.x = 100
baraban.rect.y = 0
all_sprites.add(baraban)


def rot_center(image, rect, angle):
    """rotate an image while keeping its center"""
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)

    return rot_image, rot_rect


def on_the_drum(angle):
    if angle == 5 or angle == 185: return 'Б'
    if angle == 15 or angle == 195: return '700'
    if angle == 25 or angle == 205: return '850'
    if angle == 35 or angle == 215: return 'П'
    if angle == 45 or angle == 225: return '600'
    if angle == 55 or angle == 235: return '450'
    if angle == 65 or angle == 245: return 'х2'
    if angle == 75 or angle == 255: return '800'
    if angle == 85 or angle == 265: return '950'
    if angle == 95 or angle == 275: return '+'
    if angle == 105 or angle == 285: return '400'
    if angle == 115 or angle == 295: return '650'
    if angle == 125 or angle == 305: return '0'
    if angle == 135 or angle == 315: return '500'
    if angle == 145 or angle == 325: return '750'
    if angle == 165 or angle == 345: return '350'
    if angle == 175 or angle == 355: return '1000'
    if angle == 155: return 'КЛЮЧ'
    if angle == 335: return 'Ш'


t = 5
print(on_the_drum(t))
baraban.image, baraban.rect = rot_center(img_baraban, baraban.rect, t)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if t + 10 > 355:
                t = 5
            else:
                t += 10
            print(on_the_drum(t))
            baraban.image, baraban.rect = rot_center(img_baraban, baraban.rect, t)

    screen.fill(pygame.Color("black"))

    all_sprites.draw(screen)
    poligon_points = [(0, 250), (0, 350), (180, 300)]
    pygame.draw.polygon(screen, "green", poligon_points)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(50)

pygame.quit()
