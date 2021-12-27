import os
import random
import sys
import pygame

pygame.init()
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)
SCREEN = screen
pygame.display.set_caption('Игра Поле чудес!')
clock = pygame.time.Clock()
FPS = 50
screen_rect = (0, 0, width, height)
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


def terminate():
    pygame.quit()
    sys.exit()


def create_particles(position, grav=1):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers), grav)


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
            if event.type == pygame.MOUSEBUTTONDOWN:
                # создаём частицы по щелчку мыши
                create_particles(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                return  # начинаем игру

        all_sprites.update()
        screen.fill((0, 0, 0))
        screen.blit(fon, (0, 0))
        screen.blit(string_rendered, intro_rect)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy, GRAVITY=1):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


class Difficulty_selection:  # выбор сложности
    def get_click(self, mouse_pos):
        x, y = mouse_pos
        # приобразование для упращения
        c0, c1, c2, c3 = self.customizable_coords
        n0, n1, n2, n3 = self.normal_coords
        h0, h1, h2, h3 = self.hard_coords
        # определение на какую клавишу нажато
        if x in range(c0, c0 + c2) and y in range(c1, c1 + c3):
            return "Собственная сложность"
        if x in range(n0, n0 + n2) and y in range(n1, n1 + n3):
            return "Средняя сложность"
        if x in range(h0, h0 + h2) and y in range(h1, h1 + h3):
            return "Хард кооооооооорррр!!!"
        else:
            return 0

    def render(self, screen):
        fon = pygame.transform.scale(load_image('fon1.jpg'), (width, height))  # Создание фона
        screen.blit(fon, (0, 0))

        # Абсолютно всё прописание текста нужно отредактировать под размеры окна

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
        pygame.draw.rect(screen, 'Blue', self.customizable_coords)

        self.normal_coords = (n_x + width // 3, n_y, width // 3 - 50, height // 2)
        pygame.draw.rect(screen, 'Orange', self.normal_coords)

        self.hard_coords = (n_x + (width // 3 * 2), n_y, width // 3 - 50, height // 2)
        pygame.draw.rect(screen, 'Red', self.hard_coords)

    def start(self, screen):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # создаём частицы по щелчку мыши
                    create_particles(pygame.mouse.get_pos(), 2)
                elif event.type == pygame.MOUSEBUTTONUP:
                    complexity = self.get_click(event.pos)
                    if complexity != 0:
                        return complexity  # Задаем сложность и начинаем игру
                    else:
                        print('Выберите одну из сложностей')
            all_sprites.update()
            screen.fill((0, 0, 0))
            self.render(screen)
            all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


start_screen()
hard = Difficulty_selection().start(screen)


def test(screen, poke=" "):  # Функция отображения вводимых данных
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 50)
    text = font.render(poke, True, (100, 255, 100))
    text_x = width // 2 - text.get_width() // 2
    text_y = height // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                           text_w + 20, text_h + 20), 1)


text = ""
test(screen)

font = pygame.font.Font(None, 50)
text_hard = font.render(hard, True, (100, 255, 100))

ru_letters = 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                q = len(text)
                text = text[:q - 1]
                test(screen, text)
            elif event.unicode in ru_letters:
                text += event.unicode
                test(screen, text)
            else:
                print('Можно вводить только русские буквы')
    screen.blit(text_hard, (20, 20))
    pygame.display.flip()
    clock.tick(50)

pygame.quit()
