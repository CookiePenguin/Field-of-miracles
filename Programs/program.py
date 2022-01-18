import os
import random
import sys
import pygame
import sqlite3
from random import sample, choice
import time

pygame.init()
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)
SCREEN = screen
pygame.display.set_caption('Игра Поле чудес!')
clock = pygame.time.Clock()
FPS = 60
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


def rot_center(image, rect, angle):  # Поворачиваем изображение барабана, сохраняя его центр
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect


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


class Start_screen():  # 1 окно запуска игры
    def render_start_screen(self):
        # создание фона
        fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
        # настройка надписи
        font = pygame.font.Font(None, 50)
        text = font.render("(для продолжения нажмите любую клавишу)", 1, pygame.Color('white'))
        text_rect = text.get_rect(center=(width / 2, height - 50))
        SCREEN.blit(fon, (0, 0))
        SCREEN.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:  # создаём частицы по щелчку мыши
            create_particles(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            screen_name = name_screens["Second window"]  # начинаем игру
            main_game(screen_name)

    def update(self):  # функция запускающая другие функции
        all_sprites.update()
        SCREEN.fill((0, 0, 0))

        self.render_start_screen()

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    def draw(self):
        pass


class Difficulty_selection():  # 2 окно меню
    def get_click(self, mouse_pos):
        x, y = mouse_pos
        # приобразование для упращения
        c0, c1, c2, c3 = self.customizable_coords
        n0, n1, n2, n3 = self.normal_coords
        h0, h1, h2, h3 = self.hard_coords
        # определение на какую клавишу нажато
        if x in range(c0, c0 + c2) and y in range(c1, c1 + c3):
            self.statistics_window()
        if x in range(n0, n0 + n2) and y in range(n1, n1 + n3):
            screen_name = name_screens["Input_name"]
            main_game(screen_name)
        if x in range(h0, h0 + h2) and y in range(h1, h1 + h3):
            self.rules()

    def render(self, screen):
        # создание фона
        fon = pygame.transform.scale(load_image('fon1.jpg'), (width, height))
        screen.blit(fon, (0, 0))

        font_rule3 = pygame.font.Font(None, 100)
        hard_text = font_rule3.render("Меню", True, pygame.Color('white'))
        hard_cord = hard_text.get_rect(center=(width / 2, 100))
        screen.blit(hard_text, hard_cord)
        # прорисовка кнопок
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
        R_button_text = ["Правила"]
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

        SCREEN.fill("#a7d4d0")
        SCREEN.blit(rulle_text1, rulle_cord1)
        SCREEN.blit(text, text_rect)

        intro_text = ["Вначале каждого раунда Вам необходимо выбрать уровень и тему вопросов.",
                      "Каждый раунд игры состоит из 5 вопросов, распределённых по уровням.",
                      "На экран выводится вопрос, ответ на который (загаданное слово) скрыт на табло.",
                      "Длина слова известна - каждая скрытая буква отображена на поле сиреневыми квадратиками.",
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
            SCREEN.blit(string_rendered, intro_rect)
        # цикл отрисовки
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    return  # начинаем игру
            pygame.display.flip()
            clock.tick(FPS)

    def statistics_window(self):
        font_rule = pygame.font.Font(None, 100)
        rulle_text1 = font_rule.render("Статистика", True, pygame.Color('red'))
        rulle_cord1 = rulle_text1.get_rect(center=(width / 2, 150))

        font1 = pygame.font.Font(None, 50)
        text = font1.render("(для продолжения нажмите любую клавишу)", 1, pygame.Color('red'))
        text_rect = text.get_rect(center=(width / 2, height - 100))

        SCREEN.fill("#fdbdba")
        SCREEN.blit(rulle_text1, rulle_cord1)
        SCREEN.blit(text, text_rect)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    return  # начинаем игру
            pygame.display.flip()
            clock.tick(FPS)

    def update(self):  # функция запускающая другие функции
        all_sprites.update()
        screen.fill((0, 0, 0))

        self.render(screen)

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.MOUSEBUTTONUP:
            create_particles(pygame.mouse.get_pos(), 2)
            complexity = self.get_click(event.pos)

    def draw(self):
        pass


input_name_ = ""


class Input_name:
    def __init__(self):
        self.text_input_name = ""
        self.flag_len_name = False

    def render_name_screen(self):
        # создание фона
        fon = pygame.transform.scale(load_image('fon1.jpg'), (width, height))
        # настройка надписи
        font = pygame.font.Font(None, 50)
        text = font.render('(для продолжения нажмите "OK")', 1, pygame.Color('white'))
        text_rect = text.get_rect(center=(width / 2, height - 50))
        SCREEN.blit(fon, (0, 0))
        SCREEN.blit(text, text_rect)
        pygame.draw.rect(screen, (255, 255, 255), (555, 470, 125, 45), 0)
        btn_text_input_word = 'OK'
        font = pygame.font.Font(None, 30)
        btn_text_input = font.render(btn_text_input_word, False, (0, 0, 0))
        screen.blit(btn_text_input, (600, 485))
        self.btn_answer = pygame.Rect(555, 470, 125, 45)

    def do_hints(self, screen):  # подсказки
        hints_input_name = 'Введите имя'
        font = pygame.font.SysFont('Arial Black', 50)
        hints = font.render(hints_input_name, 1, (255, 255, 255))
        screen.blit(hints, (450, 200))
        if self.flag_len_name:
            text_exit_ = 'Имя не может быть больше 9 символов'
            font = pygame.font.SysFont("Aria", 35)
            text_hints = font.render(text_exit_, 1, (230, 230, 250))
            screen.blit(text_hints, (400, 425))

    def test(self):  # функция отображения вводимых данных
        font = pygame.font.Font(None, 50)
        text = font.render(self.text_input_name, True, "white")
        text_h = text.get_height()
        screen.blit(text, (410, 360))
        pygame.draw.rect(screen, (255, 255, 255), (400, 350, 450, text_h + 20), 3)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:  # создаём частицы по щелчку мыши
            create_particles(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                q = len(self.text_input_name)
                self.text_input_name = self.text_input_name[:q - 1]
            elif len(self.text_input_name) <= 9:
                self.text_input_name += event.unicode
                global input_name_
                input_name_ = self.text_input_name
            elif len(self.text_input_name) > 9:
                self.flag_len_name = True
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.btn_answer.collidepoint(x, y):
                    screen_name = name_screens["Third window"]
                    main_game(screen_name)

    def update(self):  # функция запускающая другие функции
        all_sprites.update()
        SCREEN.fill((0, 0, 0))

        self.render_name_screen()
        self.test()
        self.do_hints(screen)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    def draw(self):
        pass


# col_question - номер вопроса из пяти возможных вопросов
COL_QUESTION = 1
# rand - список с числами без повторения
rand = sample(range(0, 19, 2), 5)
# Подготовка отображения картинки барабана на основном экране
img_baraban = load_image('барабан.png')
baraban = pygame.sprite.Sprite()
baraban.image = pygame.transform.scale(img_baraban, (250, 250))
baraban.rect = baraban.image.get_rect()
baraban.rect.x = 975
baraban.rect.y = 525
# Список никнейм ботов
spusok_name = ["any123", "АНТОНина", "ДЖОН", "Güneş", "ingquza", "Kirill", "Anastasia", "Маша", "Вика", "дима2019",
               "20Максим10", "никита", "ybrbnf", "серый", "лолита:3", "кошка", "Женя"]
# Словарь для связи картинки (аватарки) и никнейма ботов
photo_spusok_name = {"any123": "Photo_girl1.png", "АНТОНина": "Photo_girl2.jpg", "ДЖОН": "Photo_boy2.jpg",
                     "Güneş": "Photo_girl3.png", "ingquza": "Photo_girl2.jpg", "Kirill": 'Photo_boy3.png',
                     "Anastasia": "Photo_girl1.png", "Маша": "Photo_girl3.png", "Вика": "Photo_girl1.png",
                     "дима2019": "Photo_boy3.png", "20Максим10": "Photo_boy2.jpg",
                     "никита": "Photo_boy2.jpg", "ybrbnf": "Photo_name_1.jpg", "серый": "Photo_name_1.jpg",
                     "лолита:3": "Photo_girl1.png", "кошка": "Photo_girl2.jpg", "Женя": "Photo_name_1.jpg"}
# Рандомный выбор участвующих ботов в уровне
random_number = random.sample(range(0, 16), 2)
# Подготовка аварки ботов к отображению на экране
picture_1 = load_image(photo_spusok_name[spusok_name[random_number[0]]])
picture1 = pygame.transform.scale(picture_1, (75, 75))

picture_2 = load_image(photo_spusok_name[spusok_name[random_number[1]]])
picture2 = pygame.transform.scale(picture_2, (75, 75))

ru_letters = 'йцукенгшщзхъфывапролджэячсмитьбюАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЫЭЮЯ'


class Window_game:  # Основное окно игры
    def __init__(self):  # Инцилизация класса
        self.t = 5
        self.text = ""
        self.col_mark = 0
        self.col_mark_1_robot = 0
        self.col_mark_2_robot = 0
        self.flag = 0
        self._ww = 16
        self._hh = 5
        self.left = 200
        self.top = 100
        self.cell_size = 50
        self.bykva = ""
        # self.col_question = col_question
        self.flag_input_word = False
        #  self.word_guessed = word_guessed
        self.slovar_guessed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.slovar2_guessed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.slovar3_guessed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.flag1_bot_choice = False
        self.flag2_bot_choice = False
        self.flag_gamer_choice = False
        self.flag_first = True
        self.flag_random = False

        # Из базы данных отбираем записи (слова и вопросы)
        con = sqlite3.connect("questions_db (2).sqlite")
        cur = con.cursor()
        word11 = cur.execute(f"""SELECT questionandword.woords, questionandword.qquestion
                           FROM questionandword, level JOIN level_question
                           ON questionandword.num = level_question.id_question AND
                           level.id = level_question.id_level
                           WHERE id_level = {COL_QUESTION}""").fetchall()
        con.close()
        word_question = []
        self.questionn1 = ''
        for i in word11:
            for j in i:
                word_question.append(j)
        # Из полученной выборки случайным образом определяем пару загаданное слово и вопрос к нему
        # Загаданное слово word и вопрос относящийся к нему questionn1
        self.word = word_question[rand[COL_QUESTION - 1]]
        self.questionn1 = word_question[rand[COL_QUESTION - 1] + 1]
        self.word_guessed = len(self.word) * " "

    def render_field(self, screen):  # рендер окна
        # Рисуем основное поле с загаданным словом
        self.board = [[0] * width for i in range(height)]
        for i in range(self._hh):
            for j in range(self._ww):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255),
                                 (j * self.cell_size + self.left, i * self.cell_size + self.top, self.cell_size,
                                  self.cell_size), 0)
        self.question_and_word(screen)
        for i in range(self._hh):
            for j in range(self._ww):
                pygame.draw.rect(screen, pygame.Color(0, 0, 0),
                                 (j * self.cell_size + self.left, i * self.cell_size + self.top, self.cell_size,
                                  self.cell_size), 1)
        # Устанавливаем барабан
        baraban.image, baraban.rect = rot_center(img_baraban, baraban.rect, self.t)
        if baraban not in all_sprites:
            all_sprites.add(baraban)
        # Отображаем полученный баллы за раунды
        pygame.draw.rect(screen, (102, 0, 255), (1100, 0, 100, 50), 0)
        font = pygame.font.Font(None, 55)
        text = font.render(str(self.col_mark), False, (255, 204, 0))
        screen.blit(text, (1125, 10))
        # Рисовка "кнопки" выхода
        exit_picture = load_image('exit_picture.jpg')
        exit_picture = pygame.transform.scale(exit_picture, (85, 40))
        screen.blit(exit_picture, (0, 0))
        self.rect = pygame.Rect(0, 0, 85, 40)
        # Рисовка поля с выбором буквы или вводом слова целиком
        pygame.draw.rect(screen, (102, 0, 255), (200, 450, 520, 325), 5)
        self.slovar = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й']
        self.slovar2 = ['К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф']
        self.slovar3 = ['Х', 'Ц', 'Ч', 'Ш', 'Щ', "Ъ", "Ь", "Ы", "Э", "Ю", "Я"]
        a, b, c = 220, 220, 220
        for j in range(len(self.slovar)):
            pygame.draw.rect(screen, (102, 0, 255), (a, 505, 35, 35), 3)
            font = pygame.font.Font(None, 35)
            text_start = font.render(self.slovar[j], False, (255, 255, 255))
            screen.blit(text_start, (a + 10, 510))
            if self.slovar_guessed[j] == 1:
                pygame.draw.line(screen, (255, 3, 62), (a, 505), (a + 35, 505 + 35), 3)
                pygame.draw.line(screen, (255, 3, 62), (a, 505 + 35), (a + 35, 505), 3)
            a += 45
        for j in range(len(self.slovar2)):
            pygame.draw.rect(screen, (102, 0, 255), (b, 555, 35, 35), 3)
            font = pygame.font.Font(None, 35)
            text_start = font.render(self.slovar2[j], False, (255, 255, 255))
            screen.blit(text_start, (b + 10, 560))
            if self.slovar2_guessed[j] == 1:
                pygame.draw.line(screen, (255, 3, 62), (b, 555), (b + 35, 555 + 35), 3)
                pygame.draw.line(screen, (255, 3, 62), (b, 555 + 35), (b + 35, 555), 3)
            b += 45
        for j in range(len(self.slovar3)):
            pygame.draw.rect(screen, (102, 0, 255), (c, 605, 35, 35), 3)
            font = pygame.font.Font(None, 35)
            text_start = font.render(self.slovar3[j], False, (255, 255, 255))
            screen.blit(text_start, (c + 10, 610))
            if self.slovar3_guessed[j] == 1:
                pygame.draw.line(screen, (255, 3, 62), (c, 605), (c + 35, 605 + 35), 3)
                pygame.draw.line(screen, (255, 3, 62), (c, 605 + 35), (c + 35, 605), 3)
            c += 45
        text_input_word = 'Скажите букву или слово целиком'
        font = pygame.font.SysFont('Consolas', 20)
        text_input = font.render(text_input_word, 3, (0, 0, 0))
        screen.blit(text_input, (290, 465))
        pygame.draw.rect(screen, (255, 255, 255), (400, 715, 125, 45), 0)
        btn_text_input_word = 'Ответить'
        font = pygame.font.Font(None, 30)
        btn_text_input = font.render(btn_text_input_word, False, (0, 0, 0))
        screen.blit(btn_text_input, (415, 730))
        self.btn_answer = pygame.Rect(400, 715, 125, 45)

    def question_and_word(self, screen):  # Вывод вопроса и слова на экран
        # Выводим вопрос на экран
        self.question = []
        if len(self.questionn1) >= 66:
            s = self.questionn1[:66]
            ind_pr = s.rfind(" ")
            s1 = self.questionn1[:ind_pr]
            s2 = self.questionn1[ind_pr:]
            self.question.append(s1)
            self.question.append(s2)
        else:
            self.question.append(self.questionn1)
        text_coord = 35
        for line in self.question:
            font = pygame.font.SysFont('Consolas', 25)
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect(center=(width / 2, text_coord))
            text_coord += 30
            SCREEN.blit(string_rendered, intro_rect)
        # Отрисовываем на экране клетки, равные количеству букв загаданного слова
        for j in range(8 - len(self.word) // 2, 8 - len(self.word) // 2 + len(self.word)):
            pygame.draw.rect(screen, pygame.Color(189, 51, 164),
                             (j * self.cell_size + self.left, 2 * self.cell_size + self.top, self.cell_size,
                              self.cell_size), 0)

    def test(self):  # функция отображения вводимых данных
        font = pygame.font.Font(None, 50)
        text = font.render(self.text, True, "white")
        text_x = 250
        text_y = 660
        text_h = text.get_height()

        screen.blit(text, (text_x, text_y))
        pygame.draw.rect(screen, ("blue"), (text_x - 10, text_y - 10,
                                            450, text_h + 20), 2)

    def do_hints(self, screen):  # подсказки
        # Добрыми словами встречаем игрока
        self.text_main_clue = 'Тройка игроков в студию!'
        font = pygame.font.SysFont('Arial Black', 28)
        text_clue = font.render(self.text_main_clue, 1, (0, 0, 0))
        if self.flag == 0:
            screen.blit(text_clue, (400, 355))
        # Продожить игру можно при нажатие на клавиатуре R
        text_exit_start = 'Чтобы продолжить нажмите клавишу [пробел]'
        font = pygame.font.SysFont("Aria", 25)
        text_start = font.render(text_exit_start, 1, (159, 129, 112))
        screen.blit(text_start, (430, 400))
        # Выводим имя пользователя, чтобы не забыл
        global input_name_
        font = pygame.font.SysFont('Arial Black', 22)
        text = font.render(input_name_, 1, (0, 0, 0))
        screen.blit(text, (1030, 55))
        if self.flag == 1:
            self.text = ""
            if self.flag1_bot_choice:
                self.text_main_clue = f'{spusok_name[random_number[0]]}, вращайте барабан'
            if self.flag2_bot_choice:
                self.text_main_clue = f'{spusok_name[random_number[1]]}, вращайте барабан'
            if self.flag_gamer_choice:
                self.text_main_clue = f'{input_name_}, вращайте барабан'
            font = pygame.font.SysFont('Arial Black', 28)
            text_clue = font.render(self.text_main_clue, 1, (0, 0, 0))
            screen.blit(text_clue, (400, 355))
            self.bykva = ''
        if self.flag == 2:
            self.text_main_clue = 'Выберите букву'
            font = pygame.font.SysFont('Arial Black', 24)
            text_clue = font.render(self.text_main_clue, 1, (0, 0, 0))
            screen.blit(text_clue, (495, 355))
            if self.flag1_bot_choice or self.flag2_bot_choice:
                self.flag_random = True
        if self.flag == 3:
            if self.bykva.lower() in self.word and self.bykva != "":
                self.flag = 4

            if self.bykva.lower() not in self.word and self.bykva != "":

                if self.flag1_bot_choice:
                    self.flag1_bot_choice = False
                    self.flag_gamer_choice = True
                elif self.flag_gamer_choice:
                    self.flag_gamer_choice = False
                    self.flag2_bot_choice = True
                elif self.flag2_bot_choice:
                    self.flag2_bot_choice = False
                    self.flag1_bot_choice = True
                self.flag = 5
        if self.flag == 4:
            self.text_main_clue = 'Вы отгадали одну букву!'
            font = pygame.font.SysFont('Arial Black', 24)
            text_clue = font.render(self.text_main_clue, 1, (0, 0, 0))
            screen.blit(text_clue, (495, 355))
            print(self.bykva, "098")

        if self.flag == 5:
            self.text_main_clue = 'Такой буквы в слове нет!'
            print(self.bykva + "1234")
            font = pygame.font.SysFont('Arial Black', 24)
            text_clue = font.render(self.text_main_clue, 1, (0, 0, 0))
            screen.blit(text_clue, (450, 355))

        if self.flag == 6:
            self.text_main_clue = 'ВЫ ОТГАДАЛИ СЛОВО!'
            font = pygame.font.SysFont('Arial Black', 24)
            text_clue = font.render(self.text_main_clue, 1, (0, 0, 0))
            screen.blit(text_clue, (400, 355))
        #  COL_QUESTION += 1
        if self.flag == 7:
            global COL_QUESTION
            COL_QUESTION += 1
            screen_name = name_screens["Third window"]
            main_game(screen_name)
        if self.flag == 8:
            text_n0_guessed = 'Подумайте ещё'
            font = pygame.font.SysFont('Arial Black', 24)
            n0_guessed = font.render(text_n0_guessed, 1, (0, 0, 0))
            screen.blit(n0_guessed, (450, 355))
            self.flag_gamer_choice = False
            self.flag2_bot_choice = True

    #  print(self.flag)
    #   print('бот1=', self.flag1_bot_choice, 'бот2=', self.flag2_bot_choice, 'пользователь=',
    #   self.flag_gamer_choice, 'ветка=', self.flag, 'рандом=', self.flag_random, ',буква=', self.bykva)

    # def btn_next_question(self, screen):
    #    pygame.draw.rect(screen, (102, 0, 255), (1000, 0, 225, 50), 0)
    #   text_next_question = 'Следующий вопрос'
    #  font = pygame.font.Font(None, 25)
    #   text = font.render(text_next_question, False, (255, 204, 0))
    #  screen.blit(text, (1020, 15))

    def open_letter(self, screen):
        slovo = ''

        for r in range(len(self.word)):
            if self.word[r] == self.bykva.lower():
                slovo = slovo + self.bykva
            else:
                slovo = slovo + self.word_guessed[r]
        if self.flag_input_word:
            slovo = self.word
        self.word_guessed = slovo
        for j in range(len(self.word_guessed)):
            font = pygame.font.SysFont("Aria Black", 45)
            text_word_guessed = font.render(self.word_guessed[j], 1, (0, 0, 0))
            intro_rect = (((j + 8 - len(self.word_guessed) // 2) * self.cell_size +
                           self.left) + 15, (2 * self.cell_size + self.top) + 10)
            screen.blit(text_word_guessed, intro_rect)
        if self.word_guessed.lower() == self.word:
            self.flag = 6
            print("ПРИВЕТ")

    def bots(self):  # Отображаем на эране оботов (аватарка + никнейм)
        # Рисуем фон аватарки
        pygame.draw.circle(screen, (255, 255, 255), (75, 525), 55)
        pygame.draw.circle(screen, (255, 255, 255), (75, 690), 55)
        # Отображаем на экране аватарки поверх белого круга
        rect = picture1.get_rect()
        rect.x, rect.y = 0, 0
        rect = rect.move((40, 485))
        screen.blit(picture1, rect)

        rect = picture2.get_rect()
        rect.x, rect.y = 0, 0
        rect = rect.move((40, 650))
        screen.blit(picture2, rect)
        # Подписываем
        font = pygame.font.SysFont('Arial Black', 16)
        text = font.render(spusok_name[random_number[0]], 1, (0, 0, 0))
        screen.blit(text, (45, 450))

        font = pygame.font.SysFont('Arial Black', 16)
        text = font.render(spusok_name[random_number[1]], 1, (0, 0, 0))
        screen.blit(text, (45, 615))
        # Отображаем счётчик баллов батов
        pygame.draw.rect(screen, (102, 0, 255), (35, 575, 75, 25), 0)
        pygame.draw.rect(screen, (102, 0, 255), (35, 740, 75, 25), 0)

        font = pygame.font.Font(None, 35)
        text = font.render(str(self.col_mark_1_robot), False, (255, 204, 0))
        screen.blit(text, (45, 577))
        font = pygame.font.Font(None, 35)
        text = font.render(str(self.col_mark_2_robot), False, (255, 204, 0))
        screen.blit(text, (45, 742))

        # Оживляем ботов, определяем выбранный список и букву
        # Выбор рандомного списка с русским алфавитом
        if (self.flag1_bot_choice or self.flag2_bot_choice) and self.flag == 3 and self.flag_random:
            self.flag_random = False
            # Выбор рандомного списка с русским алфавитом
            random_num_spusok_ru_lletter = random.choice(range(1, 4))
            # Выбор буквы в списки
            random_num_ru_lletter = random.choice(range(0, 11))
            print('до  ', self.slovar_guessed)
            print('до  ', self.slovar2_guessed)
            print('до  ', self.slovar3_guessed)
            if random_num_spusok_ru_lletter == 1:
                if self.slovar_guessed[random_num_ru_lletter] != 1:
                    self.bykva = self.slovar[random_num_ru_lletter]
                    self.slovar_guessed[random_num_ru_lletter] = 1
                else:
                    self.flag_random = True
            if random_num_spusok_ru_lletter == 2:
                if self.slovar2_guessed[random_num_ru_lletter] != 1:
                    self.bykva = self.slovar2[random_num_ru_lletter]
                    self.slovar2_guessed[random_num_ru_lletter] = 1
                else:
                    self.flag_random = True
            if random_num_spusok_ru_lletter == 3:
                if self.slovar3_guessed[random_num_ru_lletter] != 1:
                    self.bykva = self.slovar3[random_num_ru_lletter]
                    self.slovar3_guessed[random_num_ru_lletter] = 1
                else:
                    self.flag_random = True
            print('rand1=', random_num_spusok_ru_lletter, 'rand2=', random_num_ru_lletter)
            print('после ', self.slovar_guessed)
            print('после ', self.slovar2_guessed)
            print('после ', self.slovar3_guessed)

    def scoring(self, angle):  # Подсчёт баллов за уровень
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

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == 32:
                if self.flag == 2 and not self.flag_gamer_choice:
                    self.flag += 1
                if self.flag == 0 or self.flag == 1 or self.flag == 6 or self.flag == 8:
                    self.flag += 1

                if self.flag == 1 and self.flag_first:
                    self.flag1_bot_choice = True
                    self.flag_first = False
                if self.flag == 4 or self.flag == 5 or self.flag == 9:
                    self.flag = 1
            if event.key == pygame.K_BACKSPACE:
                q = len(self.text)
                self.text = self.text[:q - 1]
            elif event.unicode in ru_letters and self.flag_gamer_choice and self.flag == 2:
                if len(self.text) <= 11:
                    self.text += event.unicode
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    baraban.kill()
                # screen_name = name_screens["Second window"]
                # main_game(screen_name)
                if self.btn_answer.collidepoint(x, y):
                    if self.text.lower() == self.word:
                        self.flag_input_word = True
                        self.flag = 6
                    elif self.text != self.word and " " not in self.text:
                        self.flag = 8
            print(event.pos)
            if (510 <= event.pos[1] <= 645 and 230 <= event.pos[0] <= 715) and self.flag == 2:
                index_num_b = (event.pos[0] - 220 - 10) // 45
                print(index_num_b)
                if (event.pos[0] > 220 + ((index_num_b + 1) * 45) or \
                        545 < event.pos[1] < 560 or 595 < event.pos[1] < 610):
                    self.bykva = " "
                else:
                    self.x1 = 220 + index_num_b * 45
                    if 510 <= event.pos[1] <= 545:
                        self.bykva = self.slovar[index_num_b]
                        self.slovar_guessed[index_num_b] = 1
                        self.flag += 1
                    if 560 <= event.pos[1] <= 595:
                        self.bykva = self.slovar2[index_num_b]
                        self.slovar2_guessed[index_num_b] = 1
                        self.flag += 1
                    if 610 <= event.pos[1] <= 645:
                        self.bykva = self.slovar3[index_num_b]
                        self.slovar3_guessed[index_num_b] = 1
                        self.flag += 1
            else:
                self.bykva = ' '
        print(self.flag)

    def update(self):
        all_sprites.update()
        screen.fill((127, 199, 255))

        self.render_field(screen)
        self.do_hints(screen)
        self.bots()
        self.test()
        self.open_letter(screen)
        all_sprites.draw(screen)
        # Рисуем курсор для барабана
        poligon_points = [(750, 600), (750, 700), (875, 650)]
        pygame.draw.polygon(screen, "green", poligon_points)
        pygame.display.flip()
        clock.tick(FPS)

    def draw(self):
        pass


name_screens = {"First window": Start_screen(), "Second window": Difficulty_selection(), "Input_name": Input_name(),
                "Third window": Window_game()}
screen_name = name_screens["First window"]


def main_game(screen_name):
    running = True
    while running:
        for event in pygame.event.get():
            screen_name.handle_event(event)
        screen_name.update()
        screen_name.draw()

        pygame.display.flip()
        clock.tick(50)
    pygame.quit()


main_game(screen_name)  # строка запускающая всю игру
