import os
import random
import sys
import pygame

pygame.init()
# 1200 800
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


def start_screen():  # стартовое окно загрузки
    # создание фона
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))

    # настройка надписи
    font = pygame.font.Font(None, 50)
    text = font.render("(для продолжения нажмите любую клавишу)", 1, pygame.Color('white'))
    text_rect = text.get_rect(center=(width / 2, height - 50))
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
        screen.blit(text, text_rect)
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


class Difficulty_selection:  # 2 окно выбора сложности
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
        # создание фона
        fon = pygame.transform.scale(load_image('fon1.jpg'), (width, height))
        screen.blit(fon, (0, 0))

        # Абсолютно всё прописание текста нужно отредактировать под размеры окна

        # настройка текста
        font_rule2 = pygame.font.Font(None, 70)
        rulle_text2 = font_rule2.render("Чтобы прочитать правила нажмите клавишу [P]", True, pygame.Color('white'))
        rulle_cord2 = rulle_text2.get_rect(center=(width / 2, height - 100))
        screen.blit(rulle_text2, rulle_cord2)

        font_rule3 = pygame.font.Font(None, 100)
        hard_text = font_rule3.render("Меню", True, pygame.Color('white'))
        hard_cord = hard_text.get_rect(center=(width / 2, 100))
        screen.blit(hard_text, hard_cord)

        # прорисовка кнопок сложности
        # константы
        n_x = 25
        n_y = 250
        const = width // 3 - 50
        font_button_text = pygame.font.Font(None, 40)
        # синяя кнопка
        self.customizable_coords = (n_x, n_y, const, const)
        pygame.draw.rect(screen, 'Blue', self.customizable_coords)
        B_button_text = ["Статистика"]
        text_coord = n_y + const / 4
        for line in B_button_text:
            string_rendered = font_button_text.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect(center=((n_x + (const / 2), text_coord)))
            text_coord += 40
            screen.blit(string_rendered, intro_rect)
        # оранжевая кнопка
        self.normal_coords = (n_x + width // 3, n_y, const, const)
        pygame.draw.rect(screen, "#3caa3c", self.normal_coords)
        O_button_text = ["Новая игра"]
        text_coord = n_y + const / 4
        for line in O_button_text:
            string_rendered = font_button_text.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect(center=(width / 2, text_coord))
            text_coord += 50
            screen.blit(string_rendered, intro_rect)
        # красная кнопка
        self.hard_coords = (n_x + (width // 3 * 2), n_y, const, const)
        pygame.draw.rect(screen, 'Red', self.hard_coords)
        R_button_text = ["Правила" ]
        text_coord = n_y + const / 4
        for line in R_button_text:
            string_rendered = font_button_text.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect(center=((n_x + (width // 3 * 2)) + const / 2, text_coord))
            text_coord += 50
            screen.blit(string_rendered, intro_rect)

    def rules(self):
        # настройка надписей
        font_rule = pygame.font.Font(None, 100)
        rulle_text1 = font_rule.render("Правила игры", True, pygame.Color('red'))
        rulle_cord1 = rulle_text1.get_rect(center=(width / 2, 150))

        font1 = pygame.font.Font(None, 50)
        text = font1.render("(для продолжения нажмите любую клавишу)", 1, pygame.Color('red'))
        text_rect = text.get_rect(center=(width / 2, height - 100))

        screen.fill("#a7d4d0")
        screen.blit(rulle_text1, rulle_cord1)
        screen.blit(text, text_rect)

        intro_text = ["Вначале каждого раунда Вам необходимо выбрать уровень и тему вопросов.",
                      "Каждый раунд игры состоит из 5 вопросов, посвященных выбранной теме.",
                      "На экран выводится вопрос, ответ на который (загаданное слово) скрыт на табло.",
                      "Длина слова известна - каждая скрытая буква отображена на поле квадратиками.",
                      "Выбор буквы осуществляется наведением курсора на соответствующую букву",
                      "и нажатием левой кнопки мыши.",
                      "Если выбранная буква есть в загаданном слове, то она будет открыта.",
                      "Если Вы знаете ответ - полное слово, то введите его в поле для ввода ответа",
                      "и нажмите кнопку Проверить.",
                      "Основная задача игрока - угадать загаданное слово раньше соперников."]

        font2 = pygame.font.Font(None, 35)
        text_coord = 250
        for line in intro_text:
            string_rendered = font2.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect(center=(width / 2, text_coord))
            text_coord += 40
            screen.blit(string_rendered, intro_rect)
        # цикл отрисовки
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    return # начинаем игру
            pygame.display.flip()
            clock.tick(FPS)

    def start(self, screen):  # функция запускающая другие функции
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
                        # Задаем сложность и начинаем игру
                        return complexity
                    else:
                        print('Выберите одну из сложностей')
                if event.type == pygame.KEYDOWN:
                    if event.key == 112:
                        self.rules()
            all_sprites.update()
            screen.fill((0, 0, 0))
            self.render(screen)
            all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


start_screen()
hard = Difficulty_selection().start(screen)

class Window_game:
    def __init__(self, width, height):
        self._ww = width
        self._hh = height
        self.board = [[0] * width for i in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.word = "слово123456"
        self.word_guessed = len(self.word) * " "
        self.bykva = "о"

    def render(self, screen):
        for i in range(self._hh):
            for j in range(self._ww):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255),
                                 (j * self.cell_size + self.left, i * self.cell_size + self.top, self.cell_size,
                                  self.cell_size), 0)
        for j in range(8 - len(self.word) // 2, 8 - len(self.word) // 2 + len(self.word)):
            pygame.draw.rect(screen, pygame.Color(0, 255, 255),
                             (j * self.cell_size + self.left, 2 * self.cell_size + self.top, self.cell_size,
                              self.cell_size), 0)

        for i in range(self._hh):
            for j in range(self._ww):
                pygame.draw.rect(screen, pygame.Color(0, 0, 0),
                                 (j * self.cell_size + self.left, i * self.cell_size + self.top, self.cell_size,
                                  self.cell_size), 1)

    def view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def question(self, screen):
        questionn = ["dghjcfghjklbnm,.ghjklghjkl;hjkl"]
        font2 = pygame.font.Font(None, 35)
        text_coord = 50
        for line in questionn:
            string_rendered = font2.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect(center=(1200 / 2, text_coord))
            text_coord += 40
            screen.blit(string_rendered, intro_rect)

    def test(self, screen, poke=" "):
        text = ""
        font = pygame.font.Font(None, 50)
        text_hard = font.render(hard, True, (100, 255, 100))       
        font = pygame.font.Font(None, 50)
        text = font.render(poke, True, (100, 255, 100))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                               text_w + 20, text_h + 20), 1)

    def open_letter(self, screen):
        slovo = ''
        for r in range(len(self.word)):
            if self.word[r] == self.bykva:
                slovo = slovo + self.bykva
            else:
                slovo = slovo + self.word_guessed[r]
        self.word_guessed = slovo
     #   text_coord = 8 - len(self.word) // 2
        for i in range(0, len(self.word)):
            font = pygame.font.Font(None, 60)
            string_rendered = font.render(self.word_guessed[i], 1, pygame.Color("black"))
            intro_rect = string_rendered.get_rect(center=(955 / 2, 225))
            screen.blit(string_rendered, intro_rect)


def gamme():
    pygame.init()
    size = 1200, 800
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("клеточки")
    board = Window_game(16, 5)
    board.view(200, 100, 50)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            screen.fill((127, 199, 255))
            board.render(screen)
            board.question(screen)
            board.open_letter(screen)
            board.test(screen)
            pygame.display.flip()
    pygame.quit()
gamme()



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
