import os
import sys
import pygame

pygame.init()
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Игра Поле чудес!')
clock = pygame.time.Clock()
FPS = 50


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


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))  # Создание фона
    screen.blit(fon, (0, 0))

    intro_text = ["(для продолжения нажмите любую клавишу)"]
    font = pygame.font.Font(None, 50)  # настройка размера шрифта
    text_coord = 730
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = height // 2 - 175
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


class difficulty_selection:  # выбор сложности

    def get_click(self, mouse_pos):
        x, y = mouse_pos
        # приобразование для упращения
        c0, c1, c2, c3 = self.customizable_coords
        n0, n1, n2, n3 = self.normal_coords
        h0, h1, h2, h3 = self.hard_coords
        # определение на какую клавишу нажато
        if x in range(c0, c0 + c2) and y in range(c1, c1 + c3):
            return 'customizable_coords'
        if x in range(n0, n0 + n2) and y in range(n1, n1 + n3):
            return 'normal_coords'
        if x in range(h0, h0 + h2) and y in range(h1, h1 + h3):
            return 'hard_coords'
        else:
            return 'Выберите одну из сложностей'

    def render(self, screen):
        fon = pygame.transform.scale(load_image('fon1.jpg'), (width, height))  # Создание фона
        screen.blit(fon, (0, 0))

        font_rule = pygame.font.Font(None, 75)  # настройка размера шрифта
        string_rendered = font_rule.render("Правила игры", True, pygame.Color('white'))
        screen.blit(string_rendered, (440, 50))

        rules_text = ["Отгадывайте слова",
                      "Получайте баллы",
                      "Выигрывайте призы!"]
        font_rules = pygame.font.Font(None, 50)
        text_coord = 50
        for line in rules_text:
            string_rendered = font_rules.render(line, 1, pygame.Color('white'))
            intro_rect = (text_coord, 150)
            text_coord += 350
            screen.blit(string_rendered, intro_rect)

        font_rule = pygame.font.Font(None, 75)  # настройка размера шрифта
        string_rendered = font_rule.render("Выбор сложности", True, pygame.Color('white'))
        screen.blit(string_rendered, (375, 250))

        n_x = 25
        n_y = 350

        self.customizable_coords = (n_x, n_y, width // 3 - 50, height // 2)
        print(self.customizable_coords)
        pygame.draw.rect(screen, 'Blue', self.customizable_coords)

        self.normal_coords = (n_x + width // 3, n_y, width // 3 - 50, height // 2)
        pygame.draw.rect(screen, 'Orange', self.normal_coords)

        self.hard_coords = (n_x + (width // 3 * 2), n_y, width // 3 - 50, height // 2)
        pygame.draw.rect(screen, 'Red', self.hard_coords)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEBUTTONUP:
                    complexity = self.get_click(event.pos)
                    if complexity != 'Выберите одну из сложностей':
                        print(complexity)
                        return  # начинаем игру
                    else:
                        print('Выберите одну из сложностей')
            pygame.display.flip()
            clock.tick(FPS)


# start_screen()
difficulty_selection().render(screen)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(pygame.Color("black"))
    pygame.display.flip()
    clock.tick(50)

pygame.quit()
