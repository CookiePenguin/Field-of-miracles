import os
import random
import sys
import pygame
import sqlite3
from random import sample
import shelve

pygame.init()
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)
SCREEN = screen
pygame.display.set_caption('Игра Поле чудес!')
clock = pygame.time.Clock()
FPS = 60
screen_rect = (0, 0, width, height)
all_sprites = pygame.sprite.Group()

# заготовки для барабана
USEREVENT = pygame.K_SPACE
INTRO_DURATION = random.choice(range(2, 4))  # как долго крутить барабан в секундах
TICK = USEREVENT + 1
pygame.time.set_timer(TICK, 1000)  # запускать событие (галочку) каждую секунду
time_in_seconds = INTRO_DURATION
# прописывание звуков игры
sound_hi = pygame.mixer.Sound('data/pole_players.mp3')
sound_scroll = pygame.mixer.Sound('data/scroll.mp3')
sound_letter_core = pygame.mixer.Sound('data/pole_letter_correct.mp3')
sound_letter_wrong = pygame.mixer.Sound('data/pole_letter_wrong.mp3')
sound_avtomobil = pygame.mixer.Sound('data/avtomobil.mp3')


def load_image(name, colorkey=None):  # проверка нахождения картинки в папке data
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


class Save:
    def __init__(self):
        self.file = shelve.open("save")

    def save(self):
        self.file["input_name"] = input_name_

    def add(self, name, value):
        self.file[name] = value

    def get(self, name):
        return self.file[name]

    def __del__(self):
        self.file.close()


class Particle(pygame.sprite.Sprite):  # отображение звёдочек при нажатие на левую клавишу мышки
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


class Start_screen:  # 1 окно запуска игры
    def render_start_screen(self):
        # создание фона
        fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
        # настройка надписи
        font = pygame.font.Font(None, 50)
        text = font.render("(для продолжения нажмите любую клавишу)", True, pygame.Color('white'))
        text_rect = text.get_rect(center=(width / 2, height - 50))
        SCREEN.blit(fon, (0, 0))
        SCREEN.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:  # создаём частицы по щелчку мыши
            create_particles(pygame.mouse.get_pos(), 5)
        elif event.type == pygame.KEYDOWN:
            pygame.mixer.music.stop()
            screen_name = name_screens["Second window"]  # начинаем игру
            main_game(screen_name)

    def update(self):  # функция запускающая другие функции
        all_sprites.update()
        SCREEN.fill((0, 0, 0))

        self.render_start_screen()

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    def music(self):
        pygame.mixer.music.load('data/opening_old.mp3')
        pygame.mixer.music.play(1)


# флаг только при первом вхождение в игру
FLAG_FIRST = True


class Difficulty_selection():  # 2 окно меню
    def get_click(self, mouse_pos):
        x, y = mouse_pos
        # приобразование для упращения
        c0, c1, c2, c3 = self.customizable_coords
        n0, n1, n2, n3 = self.normal_coords
        h0, h1, h2, h3 = self.hard_coords
        # определение на какую клавишу нажато
        if x in range(c0, c0 + c2) and y in range(c1, c1 + c3):
            screen_name = name_screens["HighScore"]
            main_game(screen_name)
        if x in range(n0, n0 + n2) and y in range(n1, n1 + n3):
            if FLAG_FIRST:
                screen_name = name_screens["Input_name"]
                main_game(screen_name)
            else:
                pygame.mixer.music.stop()
                screen_name = name_screens["Third window"]
                main_game(screen_name)
        if x in range(h0, h0 + h2) and y in range(h1, h1 + h3):
            self.rules()

    def render(self, screen):
        # создание фона
        fon = pygame.transform.scale(load_image('fon1.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        # настройка надписи
        font_rule3 = pygame.font.Font(None, 100)
        hard_text = font_rule3.render("Меню", False, pygame.Color('white'))
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
            string_rendered = font_button_text.render(line, False, pygame.Color('white'))
            intro_rect = string_rendered.get_rect(center=((n_x + (const / 2), text_coord)))
            text_coord += 40
            screen.blit(string_rendered, intro_rect)

        # оранжевая кнопка
        self.normal_coords = (n_x + width // 3, n_y, const, const)
        pygame.draw.rect(screen, "#3caa3c", self.normal_coords)
        if not FLAG_FIRST:
            O_button_text = ["Продолжить игру"]
        else:
            O_button_text = ["Новая игра"]
        text_coord = n_y + const / 4
        for line in O_button_text:
            string_rendered = font_button_text.render(line, False, pygame.Color('white'))
            intro_rect = string_rendered.get_rect(center=(width / 2, text_coord))
            text_coord += 50
            screen.blit(string_rendered, intro_rect)

        # красная кнопка
        self.hard_coords = (n_x + (width // 3 * 2), n_y, const, const)
        pygame.draw.rect(screen, 'Red', self.hard_coords)
        R_button_text = ["Правила"]
        text_coord = n_y + const / 4
        for line in R_button_text:
            string_rendered = font_button_text.render(line, False, pygame.Color('white'))
            intro_rect = string_rendered.get_rect(center=((n_x + (width // 3 * 2)) + const / 2, text_coord))
            text_coord += 50
            screen.blit(string_rendered, intro_rect)

    def rules(self):  # окно с правилами игры
        # настройка надписей
        font_rule = pygame.font.Font(None, 100)
        rulle_text1 = font_rule.render("Правила игры", False, pygame.Color('red'))
        rulle_cord1 = rulle_text1.get_rect(center=(width / 2, 150))

        font1 = pygame.font.Font(None, 50)
        text = font1.render("(для продолжения нажмите любую клавишу)", False, pygame.Color('red'))
        text_rect = text.get_rect(center=(width / 2, height - 100))

        SCREEN.fill("#a7d4d0")
        SCREEN.blit(rulle_text1, rulle_cord1)
        SCREEN.blit(text, text_rect)

        intro_text = ["Вначале каждого раунда Вам необходимо ввести имя.",
                      "Каждый раунд игры состоит из 5 вопросов, распределённых по уровням.",
                      "На экран выводится вопрос, ответ на который (загаданное слово) скрыт на табло.",
                      "Длина слова известна - каждая скрытая буква отображена на поле сиреневыми квадратиками.",
                      "Выбор буквы осуществляется наведением курсора на соответствующую букву",
                      "и нажатием левой кнопки мыши.",
                      "Если выбранная буква есть в загаданном слове, то она будет открыта.",
                      "Если Вы знаете ответ - полное слово, то введите его в поле для ввода ответа",
                      'и нажмите кнопку "Ответить".',
                      "Основная задача игрока - угадать загаданное слово раньше соперников."]

        font2 = pygame.font.Font(None, 35)
        text_coord = 250
        for line in intro_text:
            string_rendered = font2.render(line, False, pygame.Color('black'))
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

    def handle_event(self, event):
        global complexity
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.MOUSEBUTTONUP:
            create_particles(pygame.mouse.get_pos(), 2)
            complexity = self.get_click(event.pos)

    def update(self):  # функция запускающая другие функции
        all_sprites.update()
        screen.fill((0, 0, 0))

        self.render(screen)

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    def music(self):
        pygame.mixer.music.load('data/menu.mp3')
        pygame.mixer.music.play(-1)


class HighScore:  # окно со статистикой

    def render_statistics_window(self):
        # настройка надписи
        font_rule = pygame.font.Font(None, 100)
        rulle_text1 = font_rule.render("Статистика", False, pygame.Color('red'))
        rulle_cord1 = rulle_text1.get_rect(center=(width / 2, 150))

        font1 = pygame.font.Font(None, 50)
        text = font1.render("(для продолжения нажмите любую клавишу)", False, pygame.Color('red'))
        text_rect = text.get_rect(center=(width / 2, height - 100))

        SCREEN.fill("#fdbdba")
        SCREEN.blit(rulle_text1, rulle_cord1)
        SCREEN.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.MOUSEBUTTONUP:
            create_particles(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            screen_name = name_screens["Second window"]
            main_game(screen_name)

    def update(self):  # функция запускающая другие функции
        all_sprites.update()
        screen.fill((0, 0, 0))

        self.render_statistics_window()

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    def music(self):
        pass


# глобальная переменная для сохрания ввода имени
input_name_ = ""


class Input_name:  # 3 окно с вводом имени пользователя
    def __init__(self):
        self.text_input_name = ""
        self.flag_len_name = False

    def render_name_screen(self):
        # создание фона
        fon = pygame.transform.scale(load_image('fon1.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        # настройка надписи
        font = pygame.font.Font(None, 50)
        text = font.render('(для продолжения нажмите "OK")', False, pygame.Color('white'))
        text_rect = text.get_rect(center=(width / 2, height - 50))
        SCREEN.blit(text, text_rect)

        pygame.draw.rect(screen, (255, 255, 255), (555, 470, 125, 45), 0)

        btn_text_input_word = 'OK'
        font = pygame.font.Font(None, 30)
        btn_text_input = font.render(btn_text_input_word, False, (0, 0, 0))
        screen.blit(btn_text_input, (600, 485))
        self.btn_answer = pygame.Rect(555, 470, 125, 45)

    def do_hints(self):  # подсказки
        hints_input_name = 'Введите имя'
        font = pygame.font.SysFont('Arial Black', 50)
        hints = font.render(hints_input_name, True, (255, 255, 255))
        screen.blit(hints, (450, 200))
        if self.flag_len_name:
            text_exit_ = 'Имя не может быть больше 9 символов'
            font = pygame.font.SysFont("Aria", 35)
            text_hints = font.render(text_exit_, True, (230, 230, 250))
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
        elif event.type == pygame.KEYDOWN:  # считывание вводных данных с клавиатуры
            if event.key == pygame.K_BACKSPACE:
                q = len(self.text_input_name)
                self.text_input_name = self.text_input_name[:q - 1]
            elif len(self.text_input_name) <= 9:  # проверка на длину имени
                self.text_input_name += event.unicode
                global input_name_
                input_name_ = self.text_input_name
            elif len(self.text_input_name) > 9:
                self.flag_len_name = True
        x, y = pygame.mouse.get_pos()  # запуск следующего окна
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.btn_answer.collidepoint(x, y):
                    screen_name = name_screens["Level_selection"]
                    main_game(screen_name)

    def update(self):  # функция запускающая другие функции
        all_sprites.update()
        SCREEN.fill((0, 0, 0))

        self.render_name_screen()
        self.test()
        self.do_hints()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    def music(self):
        pass


# номер уровня из пяти возможных
level_question = 1


class Level_selection:  # 3 окно с вводом имени пользователя
    def render_level_screen(self):
        # создание фона
        fon = pygame.transform.scale(load_image('fon1.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        # настройка надписи
        hints_input_name = 'Выберите уровень'
        font = pygame.font.SysFont('Arial Black', 50)
        hints = font.render(hints_input_name, True, (255, 255, 255))
        screen.blit(hints, (400, 50))

        font = pygame.font.Font(None, 50)
        text = font.render('(для продолжения выберите уровень)', False, pygame.Color('white'))
        text_rect = text.get_rect(center=(width / 2, height - 50))
        SCREEN.blit(text, text_rect)

        pygame.draw.rect(screen, (255, 255, 255), (255, 250, 100, 100), 0)

        btn_text_level_1 = '1'
        font = pygame.font.Font(None, 65)
        btn_input_level_1 = font.render(btn_text_level_1, False, (0, 0, 0))
        screen.blit(btn_input_level_1, (295, 285))
        self.btn_level_1 = pygame.Rect(255, 250, 100, 100)

        pygame.draw.rect(screen, (255, 255, 255), (555, 250, 100, 100), 0)

        btn_text_level_2 = '2'
        btn_input_level_2 = font.render(btn_text_level_2, False, (0, 0, 0))
        screen.blit(btn_input_level_2, (595, 285))
        self.btn_level_2 = pygame.Rect(555, 250, 100, 100)

        pygame.draw.rect(screen, (255, 255, 255), (855, 250, 100, 100), 0)

        btn_text_level_3 = '3'
        btn_input_level_3 = font.render(btn_text_level_3, False, (0, 0, 0))
        screen.blit(btn_input_level_3, (895, 285))
        self.btn_level_3 = pygame.Rect(855, 250, 100, 100)

        pygame.draw.rect(screen, (255, 255, 255), (355, 450, 100, 100), 0)

        btn_text_level_4 = '4'
        btn_input_level_4 = font.render(btn_text_level_4, False, (0, 0, 0))
        screen.blit(btn_input_level_4, (395, 485))
        self.btn_level_4 = pygame.Rect(355, 450, 100, 100)

        pygame.draw.rect(screen, (255, 255, 255), (755, 450, 100, 100), 0)

        btn_text_level_5 = '5'
        btn_input_level_5 = font.render(btn_text_level_5, False, (0, 0, 0))
        screen.blit(btn_input_level_5, (795, 485))
        self.btn_level_5 = pygame.Rect(755, 450, 100, 100)

    def handle_event(self, event):
        global level_question
        if event.type == pygame.QUIT:
            terminate()
        x, y = pygame.mouse.get_pos()  # запуск следующего окна определение уровня
        if event.type == pygame.MOUSEBUTTONDOWN:
            create_particles(pygame.mouse.get_pos())  # создаём частицы по щелчку мыши
            if pygame.mouse.get_pressed()[0]:
                global level_question
                if self.btn_level_1.collidepoint(x, y):
                    pygame.mixer.music.stop()
                    screen_name = name_screens["Third window"]
                    main_game(screen_name)

                if self.btn_level_2.collidepoint(x, y):
                    level_question = 2
                    #  Window_game().__init__()
                    pygame.mixer.music.stop()
                    screen_name = name_screens["Third window"]
                    main_game(screen_name)
                if self.btn_level_3.collidepoint(x, y):
                    level_question = 3
                    # Window_game().__init__()
                    pygame.mixer.music.stop()
                    screen_name = name_screens["Third window"]
                    main_game(screen_name)
                if self.btn_level_4.collidepoint(x, y):
                    level_question = 4
                    # Window_game().__init__()
                    pygame.mixer.music.stop()
                    screen_name = name_screens["Third window"]
                    main_game(screen_name)
                if self.btn_level_5.collidepoint(x, y):
                    level_question = 5
                    Window_game().__init__()
                    pygame.mixer.music.stop()
                    screen_name = name_screens["Third window"]
                    main_game(screen_name)

    def update(self):  # функция запускающая другие функции
        all_sprites.update()
        SCREEN.fill((0, 0, 0))

        self.render_level_screen()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    def music(self):
        pass


COL_QUESTION = 1
# rand - список с числами без повторения
rand = sample(range(0, 19, 2), 5)
# Подготовка отображения картинки барабана на основном экране
img_baraban = load_image('барабан2.png')
baraban = pygame.sprite.Sprite()
baraban.image = pygame.transform.scale(img_baraban, (250, 250))
baraban.rect = baraban.image.get_rect()
baraban.rect.x = 975
baraban.rect.y = 525
# Список никнейм ботов
spusok_name = ["any123", "АНТОНина", "ДЖОН", "G?ne?", "ingquza", "Kirill", "Anastasia", "Маша", "Вика", "дима2019",
               "20Максим10", "никита", "ybrbnf", "серый", "лолита:3", "кошка", "Женя"]
# Словарь для связи картинки (аватарки) и никнейма ботов
photo_spusok_name = {"any123": "Photo_girl1.png", "АНТОНина": "Photo_girl2.jpg", "ДЖОН": "Photo_boy2.jpg",
                     "G?ne?": "Photo_girl3.png", "ingquza": "Photo_girl2.jpg", "Kirill": 'Photo_boy3.png',
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
# проверка на язык при вводе ответа целиком
ru_letters = 'йцукенгшщзхъфывапролджэячсмитьбюАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЫЭЮЯ'

# подсчет баллов
col_mark_gamer = 0
col_mark_1_robot = 0
col_mark_2_robot = 0


class Window_game:  # Основное окно игры
    def __init__(self):  # Инцилизация класса
        global INTRO_DURATION, time_in_seconds, TICK, USEREVENT, col_mark_1_robot, col_mark_2_robot, col_mark_gamer
        # отрисовка поля
        self._ww = 16
        self._hh = 5
        self.left = 200
        self.top = 100
        self.cell_size = 50
        # выделение уже выбранных букв
        self.slovar_guessed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.slovar2_guessed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.slovar3_guessed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # подсчёт баллов
        self.t = 5
        self.col_mark = 0
        self.col_mark_1_robot = col_mark_1_robot
        self.col_mark_2_robot = col_mark_2_robot
        self.flag = 0  # флаг регулирующий логику игры
        self.bykva = ""  # ввод слова по буквам
        self.text = ""  # ввод слова целиком
        self.flag_input_word = False  # флаг для проверки вводного слова
        # флаги регулирующие ход играков
        self.flag1_bot_choice = False
        self.flag2_bot_choice = False
        self.flag_gamer_choice = False
        self.flag_random = False
        self.flag_first = True
        # Заготовки для барабана
        self.flag_baraban = True
        self.intro_duration = INTRO_DURATION
        self.time_in_seconds = time_in_seconds
        self.tick = TICK
        self.userevent = USEREVENT
        self.scroll_flag = False
        # Из базы данных отбираем записи (слова и вопросы)
        con = sqlite3.connect("questions_db (2).sqlite")
        cur = con.cursor()
        word11 = cur.execute(f"""SELECT questionandword.woords, questionandword.qquestion
                           FROM questionandword, level JOIN level_question
                           ON questionandword.num = level_question.id_question AND
                           level.id = level_question.id_level
                           WHERE id_level = {level_question}""").fetchall()
        print("level_question", level_question)
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
        # сохранение
        self.save_file = Save()
        self.max_col_mark_gamer = 0
        # флаги для звуков
        self.flag_sound_hi = True
        self.flag_sound_scroll = True
        self.flag_sound_letter_wrong = True
        self.flag_sound_letter_core = True

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
        pygame.draw.rect(screen, (102, 0, 255), (1050, 0, 150, 50), 0)
        font = pygame.font.Font(None, 55)
        text = font.render(str(col_mark_gamer), False, (255, 204, 0))
        screen.blit(text, (1075, 10))
        # Рисовка "кнопки" выхода
        exit_picture = load_image('exit_picture.jpg')
        exit_picture = pygame.transform.scale(exit_picture, (85, 40))
        screen.blit(exit_picture, (0, 0))
        self.btn_exit = pygame.Rect(0, 0, 85, 40)
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
        text_input = font.render(text_input_word, True, (0, 0, 0))
        screen.blit(text_input, (290, 465))
        pygame.draw.rect(screen, (255, 255, 255), (400, 715, 125, 45), 0)
        btn_text_input_word = 'Ответить'
        font1 = pygame.font.Font(None, 30)
        btn_text_input = font1.render(btn_text_input_word, False, (0, 0, 0))
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
            string_rendered = font.render(line, True, pygame.Color('black'))
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

        if self.flag_sound_hi:
            sound_hi.play()
            self.flag_sound_hi = False
        # Добрыми словами встречаем игрока
        hints_welcome = 'Тройка игроков в студию!'
        font = pygame.font.SysFont('Arial Black', 28)
        text_welcome = font.render(hints_welcome, True, (0, 0, 0))
        global FLAG_FIRST
        if self.flag == 0 and FLAG_FIRST:
            screen.blit(text_welcome, (400, 355))
        # Продожить игру можно при нажатие на клавиатуре пробел
        text_exit_start = 'Чтобы продолжить нажмите клавишу [пробел]'
        font1 = pygame.font.SysFont("Aria", 25)
        text_start = font1.render(text_exit_start, True, (159, 129, 112))
        screen.blit(text_start, (430, 400))
        # Выводим имя пользователя, чтобы не забыл
        global input_name_
        font_name = pygame.font.SysFont('Arial Black', 22)
        text = font_name.render(input_name_, True, (0, 0, 0))
        screen.blit(text, (1050, 55))

        if self.flag == 1:  # проверяем флаг и выводим нужное имя игрока
            sound_hi.stop()
            if self.flag_sound_scroll:
                sound_scroll.play()
                self.flag_sound_scroll = False
            self.flag_sound_letter_wrong = True
            self.flag_sound_letter_core = True

            self.text = ""
            FLAG_FIRST = False
            if self.flag1_bot_choice:
                self.text_main_clue = f'{spusok_name[random_number[0]]}, вращайте барабан'
            if self.flag2_bot_choice:
                self.text_main_clue = f'{spusok_name[random_number[1]]}, вращайте барабан'
            if self.flag_gamer_choice:
                self.text_main_clue = f'{input_name_}, вращайте барабан'
            text_clue = font.render(self.text_main_clue, True, (0, 0, 0))
            screen.blit(text_clue, (400, 355))
            self.bykva = ''

        if self.flag == 2:
            self.flag_sound_scroll = True
            self.text_main_clue = 'Выберите букву'
            font2 = pygame.font.SysFont('Arial Black', 24)
            text_clue = font2.render(self.text_main_clue, True, (0, 0, 0))
            screen.blit(text_clue, (495, 355))
            if self.flag1_bot_choice or self.flag2_bot_choice:
                self.flag_random = True

        if self.flag == 3:  # проверяем буквы
            if self.bykva.lower() in self.word and self.bykva != "":
                self.flag = 4
            if self.bykva.lower() not in self.word and self.bykva != "":  # переключаем на следующего игрока
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

        if self.flag == 4:  # выводит подсказку если буква правильная и суммируем баллы
            if self.flag_sound_letter_core:
                sound_letter_core.play()
                self.flag_sound_letter_core = False
            self.text_main_clue = 'Вы отгадали одну букву!'
            font2 = pygame.font.SysFont('Arial Black', 24)
            text_clue = font2.render(self.text_main_clue, True, (0, 0, 0))
            screen.blit(text_clue, (495, 355))
            if self.flag1_bot_choice:
                global col_mark_1_robot
                col_mark_1_robot += self.col_mark
                self.col_mark_1_robot += self.col_mark
                self.col_mark = 0
            if self.flag2_bot_choice:
                global col_mark_2_robot
                col_mark_2_robot += self.col_mark
                self.col_mark_2_robot += self.col_mark
                self.col_mark = 0
            if self.flag_gamer_choice:
                global col_mark_gamer
                col_mark_gamer += self.col_mark
                self.col_mark = 0

        if self.flag == 5:  # выводит подсказку если буква не пправильная
            if self.flag_sound_letter_wrong:
                sound_letter_wrong.play()
                self.flag_sound_letter_wrong = False
            self.text_main_clue = 'Такой буквы в слове нет!'
            font5 = pygame.font.SysFont('Arial Black', 24)
            text_clue = font5.render(self.text_main_clue, True, (0, 0, 0))
            screen.blit(text_clue, (450, 355))
            self.col_mark = 0

        if self.flag == 6:  # выводим подсказку если Вы отгадали слово
            self.text_main_clue = 'ВЫ ОТГАДАЛИ СЛОВО!'
            font6 = pygame.font.SysFont('Arial Black', 24)
            text_clue = font6.render(self.text_main_clue, True, (0, 0, 0))
            screen.blit(text_clue, (400, 355))

        if self.flag == 8:  # выводим подсказку если вводное слово не верное
            text_n0_guessed = 'Подумайте ещё'
            font8 = pygame.font.SysFont('Arial Black', 24)
            n0_guessed = font8.render(text_n0_guessed, True, (0, 0, 0))
            screen.blit(n0_guessed, (450, 355))
            self.flag_gamer_choice = False
            self.flag2_bot_choice = True

    def open_letter(self, screen):  # открываем на поле угаданое слово
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
            text_word_guessed = font.render(self.word_guessed[j], True, (0, 0, 0))
            intro_rect = (((j + 8 - len(self.word_guessed) // 2) * self.cell_size +
                           self.left) + 15, (2 * self.cell_size + self.top) + 10)
            screen.blit(text_word_guessed, intro_rect)
        if self.word_guessed.lower() == self.word:
            self.flag = 6

    def bots(self, screen):  # Отображаем на эране оботов (аватарка + никнейм)
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
        text = font.render(spusok_name[random_number[0]], False, (0, 0, 0))
        screen.blit(text, (45, 450))

        text = font.render(spusok_name[random_number[1]], False, (0, 0, 0))
        screen.blit(text, (45, 615))
        # Отображаем счётчик баллов батов
        pygame.draw.rect(screen, (102, 0, 255), (35, 575, 75, 25), 0)
        pygame.draw.rect(screen, (102, 0, 255), (35, 740, 75, 25), 0)

        font = pygame.font.Font(None, 35)
        text = font.render(str(self.col_mark_1_robot), False, (255, 204, 0))
        screen.blit(text, (45, 577))

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

    def scoring(self, angle):  # Подсчёт баллов за прокрутку барабана
        if angle == 5 or angle == 185: return '450'
        if angle == 15 or angle == 195: return "700"
        if angle == 25 or angle == 205: return "850"
        if angle == 35 or angle == 215: return '150'
        if angle == 45 or angle == 225: return "600"
        if angle == 55 or angle == 235: return "450"
        if angle == 65 or angle == 245: return '250'
        if angle == 75 or angle == 255: return "800"
        if angle == 85 or angle == 265: return "950"
        if angle == 95 or angle == 275: return '200'
        if angle == 105 or angle == 285: return "400"
        if angle == 115 or angle == 295: return "650"
        if angle == 125 or angle == 305: return "10"
        if angle == 135 or angle == 315: return "500"
        if angle == 145 or angle == 325: return "750"
        if angle == 165 or angle == 345: return "350"
        if angle == 175 or angle == 355: return "1000"
        if angle == 155: return '500'
        if angle == 335: return '100'

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            terminate()

        self.save_file.save()
        self.save_file.add("max", col_mark_gamer)

        if event.type == self.tick:  # Посекундный счетчик
            self.time_in_seconds += 1

        if event.type == pygame.KEYDOWN:
            # продолжение игры при нажатии на пробел
            if event.key == pygame.K_SPACE and self.scroll_flag == False:
                if self.flag == 2 and not self.flag_gamer_choice:
                    self.flag += 1

                if self.flag == 0 or self.flag == 1 or self.flag == 6 or self.flag == 8:
                    self.flag += 1

                if self.flag == 1 and self.flag_first:  # включаем первого бота
                    self.flag1_bot_choice = True
                    self.flag_first = False

                if self.flag == 4 or self.flag == 5 or self.flag == 9:  # зацикливаем ход игры
                    self.flag = 1

                if self.flag == 7:  # переходим на следующий уровень если слово угадано
                    # global COL_QUESTION
                    # COL_QUESTION += 1
                    # if COL_QUESTION == 6:
                    #   self.max_col_mark_gamer = col_mark_gamer
                    #  baraban.kill()
                    pygame.mixer.music.stop()
                    # screen_name = name_screens["Enb_window"]
                    # main_game(screen_name)
                    self.__init__()

            if self.flag == 1:
                # выставляем случайное время кручения барабана и делаем флаг
                if event.type == pygame.KEYDOWN:
                    self.intro_duration = random.choice(range(2, 4))
                    self.flag_baraban = True
                    self.time_in_seconds = 0

            #  считывание вводных данных с клавиатуры
            if event.key == pygame.K_BACKSPACE:
                q = len(self.text)
                self.text = self.text[:q - 1]
            elif event.unicode in ru_letters and self.flag_gamer_choice and self.flag == 2:
                if len(self.text) <= 11:
                    self.text += event.unicode
        # считываем координаты нажатия на поле
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                # выход из основного окна игры в меню
                if self.btn_exit.collidepoint(x, y):
                    baraban.kill()
                    global FLAG_FIRST
                    FLAG_FIRST = False
                    screen_name = name_screens["Second window"]
                    main_game(screen_name)
                # считываем и перерабатываем вводное слово
                if self.btn_answer.collidepoint(x, y):
                    if self.text.lower() == self.word:
                        self.flag_input_word = True
                        self.flag = 6
                    elif self.text != self.word and " " not in self.text and self.text != "":
                        self.flag = 8
            if (510 <= event.pos[1] <= 645 and 230 <= event.pos[0] <= 715) and self.flag == 2 \
                    and self.flag_gamer_choice:
                index_num_b = (event.pos[0] - 220 - 10) // 45
                if (event.pos[0] > 220 + ((index_num_b + 1) * 45)
                        or 545 < event.pos[1] < 560 or 595 < event.pos[1] < 610):
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

    def update(self):
        all_sprites.update()
        screen.fill((127, 199, 255))

        self.render_field(screen)
        self.do_hints(screen)
        self.bots(screen)
        self.test()
        self.open_letter(screen)

        # вращение барабана
        if self.time_in_seconds < self.intro_duration:
            if self.t + 10 > 355:
                self.t = 5
            else:
                self.t += 10
            self.scroll_flag = True
            baraban.image, baraban.rect = rot_center(img_baraban, baraban.rect, self.t)
        # то что происходит после прокрутки барабана
        elif self.time_in_seconds == self.intro_duration:
            if self.flag_baraban:
                sound_scroll.stop()
                self.col_mark = int(self.scoring(self.t))
                self.scroll_flag = False
                self.flag_baraban = False

        all_sprites.draw(screen)
        # Рисуем курсор для барабана
        poligon_points = [(750, 600), (750, 700), (875, 650)]
        pygame.draw.polygon(screen, "green", poligon_points)
        pygame.display.flip()
        clock.tick(FPS)

    def music(self):
        pass


# заготовки для машинки
img_car = load_image('машинка2.png')
car = pygame.sprite.Sprite()
car.image = pygame.transform.scale(img_car, (400, 400))
car.rect = car.image.get_rect(center=(width / 2, height / 10 * 7))
MYEVENTTYPE = pygame.USEREVENT + 1
pygame.time.set_timer(MYEVENTTYPE, 10)


class Enb_window:
    def __init__(self):
        # заготовки для машинки
        self.flag = False
        all_sprites.add(car)
        self.flag_sound_avtomobil = True

    def render_start_screen(self):
        fon = pygame.transform.scale(load_image('win.jpg'), (width, height))
        SCREEN.blit(fon, (0, 0))
        # настройка надписи
        font = pygame.font.Font(None, 80)
        text = font.render(f"Поздравляю вы набрали {col_mark_gamer} очков!", False, pygame.Color('white'))
        text_rect = text.get_rect(center=(width / 2, height / 10 * 3))
        SCREEN.blit(text, text_rect)

        font = pygame.font.Font(None, 50)
        text1 = font.render('(для возвращения в меню нажмите любую клавишу)', False, pygame.Color('#00FA9A'))
        text_btn = text1.get_rect(center=(width / 2, height / 10 * 9))
        SCREEN.blit(text1, text_btn)

        if col_mark_gamer >= 10000:
            self.won()
        else:
            self.not_won()

    def not_won(self):
        font = pygame.font.Font(None, 50)
        text2 = font.render("К сожалению вы не набрали 10000 очков для приза", True, pygame.Color('white'))
        text_btn = text2.get_rect(center=(width / 2, height / 10 * 4))
        SCREEN.blit(text2, text_btn)

        text3 = font.render("Вы можете попробовать снова!", True, pygame.Color('white'))
        text_btn = text3.get_rect(center=(width / 2, height / 10 * 5))
        SCREEN.blit(text3, text_btn)

        self.flag_won = False

    def won(self):
        if self.flag_sound_avtomobil:
            sound_avtomobil.play()
            self.flag_sound_avtomobil = False

        font = pygame.font.Font(None, 50)
        text2 = font.render("И вы выигрываете автомобиль!!!", True, pygame.Color('white'))
        text_btn = text2.get_rect(center=(width / 2, height / 10 * 4))
        SCREEN.blit(text2, text_btn)

        text3 = font.render("Спасибо за игру)", True, pygame.Color('white'))
        text_btn = text3.get_rect(center=(width / 2, height / 10 * 5))
        SCREEN.blit(text3, text_btn)
        self.flag_won = True

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            terminate()
        if event.type == MYEVENTTYPE and self.flag_won:
            if car.rect.x <= 10:
                self.flag = True
                car.image = pygame.transform.flip(car.image, True, False)
            if car.rect.x == height - 10:
                self.flag = False
                car.image = pygame.transform.flip(car.image, True, False)
            if self.flag == True:
                car.rect.x += 5
            else:
                car.rect.x -= 5

        if event.type == pygame.MOUSEBUTTONDOWN:  # создаём частицы по щелчку мыши
            create_particles(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            car.kill()
            screen_name = name_screens["Second window"]
            main_game(screen_name)

    def update(self):  # функция запускающая другие функции
        all_sprites.update()
        SCREEN.fill("#3CB371")

        self.render_start_screen()

        if self.flag_won:
            all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    def music(self):
        pygame.mixer.music.load('data/winner-of-tour.mp3')
        pygame.mixer.music.play(1)


name_screens = {"First window": Start_screen(), "Second window": Difficulty_selection(), "Input_name": Input_name(),
                "Level_selection": Level_selection(), "Third window": Window_game(), "Enb_window": Enb_window(),
                "HighScore": HighScore()}
# костыль
if col_mark_gamer < 10000:
    car.kill()

screen_name = name_screens["First window"]


def main_game(screen_name):
    running = True
    screen_name.music()
    while running:
        for event in pygame.event.get():
            screen_name.handle_event(event)
        screen_name.update()
        pygame.display.flip()
        clock.tick(50)
    pygame.quit()


main_game(screen_name)  # строка запускающая всю игру
