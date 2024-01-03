import pygame
import sys

pygame.init()


class ImageButton:  # Воспомогательный класс для загрузки кнопок на основное окно
    def __init__(self, x, y, width, height, text, image_path, hover_image_path=None,
                 sound_path=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.hover_image = self.image
        if hover_image_path:
            self.hover_image = pygame.image.load(hover_image_path)
            self.hover_image = pygame.transform.scale(self.hover_image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.sound = None
        if sound_path:
            self.sound = pygame.mixer.Sound(sound_path)
        self.is_hovered = False

    def set_pos(self, x, y = None):
        self.x = x
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):  # Отрисовка кнопок и текста на них
        current_image = self.hover_image if self.is_hovered else self.image
        screen.blit(current_image, self.rect.topleft)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):  # Если если столкновение mouse_pos с кнопкой, то True
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):  # Отслеживание нажатия кнопки меню
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.sound:
                self.sound.play()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))


SIZE = WIDTH, HEIGHT = 1276, 717
FPS = 60
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SIZE)
background_image = pygame.image.load('data/background_main_menu.jpg')
pygame.display.set_caption('The Legend of a Kingdom')
# Загрузка и установка своего курсора
cursor = pygame.image.load("data/cursor.png")
pygame.mouse.set_visible(False)


# Воспомогательная функция изменения разрешения окна игры.
def change_video_mode(w, h, fullscreen=0):
    global screen, SIZE, WIDTH, HEIGHT, background_image
    SIZE = WIDTH, HEIGHT = w, h
    screen = pygame.display.set_mode(SIZE, fullscreen)
    background_image = pygame.image.load(f'data/background_main_menu{WIDTH}.jpg')


# Функция основного меню игры:
def main_menu():
    # Кнопки
    play_button = ImageButton(WIDTH / 2 - (252 / 2), 175, 252, 75, "", "data/start.png",
                              "data/start_pink.png", "sounds/knopka.mp3")
    settings_button = ImageButton(WIDTH / 2 - (252 / 2), 250, 252, 74, "", "data/settings.jpg",
                                  "data/settings_hover.jpg", "sounds/knopka.mp3")
    store_button = ImageButton(WIDTH / 2 - (252 / 2), 325, 252, 74, "", "data/store.jpg",
                               "", "sounds/knopka.mp3")
    quit_button = ImageButton(WIDTH / 2 - (252 / 2), 400, 252, 74, "", "data/quit.jpg",
                              "", "sounds/knopka.mp3")
    btn = [play_button, settings_button, store_button, quit_button]  # Добавление кнопок в список
    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.USEREVENT and event.button == play_button:
                print('НАЖАТА КНОПКА "play_button"')
                fade()
                new_game()

            if event.type == pygame.USEREVENT and event.button == settings_button:
                print('НАЖАТА КНОПКА "settings_button"')
                fade()
                settings_menu()

            if event.type == pygame.USEREVENT and event.button == store_button:
                print('НАЖАТА КНОПКА "store_button"')

            if event.type == pygame.USEREVENT and event.button == quit_button:
                print('НАЖАТА КНОПКА "quit_button"')
                running = False
                pygame.quit()
                sys.exit()

            for but in btn:
                but.handle_event(event)

        for but in btn:
            but.set_pos(WIDTH / 2 - (252 / 2))
            but.check_hover(pygame.mouse.get_pos())
            but.draw(screen)

        # Отрисовка курсора в текущей позиции мыши !нужно делать в каждой фукнции перед флипом!
        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


def settings_menu():
    # Создание кнопок
    audio_button = ImageButton(WIDTH / 2 - (252 / 2), 175, 252, 74, "Звук", "data/back.png",
                              "data/back_border.png", "sounds/knopka.mp3")
    video_button = ImageButton(WIDTH / 2 - (252 / 2), 249, 252, 75, "Графика", "data/back.png",
                              "data/back_border.png", "sounds/knopka.mp3")
    back_button = ImageButton(WIDTH / 2 - (252 / 2), 324, 252, 75, "Назад", "data/back.png",
                              "data/back_border.png", "sounds/knopka.mp3")
    btn = [audio_button, video_button, back_button]

    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                fade()
                main_menu()

            if event.type == pygame.USEREVENT and event.button == back_button:
                print('НАЖАТА КНОПКА "back_button"')
                fade()
                main_menu()

            if event.type == pygame.USEREVENT and event.button == video_button:
                print('НАЖАТА КНОПКА "video_button"')
                fade()
                video_settings()

            for but in btn:
                but.handle_event(event)

        for but in btn:
            but.set_pos(WIDTH / 2 - (252 / 2))
            but.check_hover(pygame.mouse.get_pos())
            but.draw(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


# Функция настроек графики. Выбор разрешения окна игры.
def video_settings():
    # Создание кнопок:
    video1_button = ImageButton(WIDTH / 2 - (252 / 2), 175, 175, 74, "960x600", "data/back.png",
                              "data/back_border.png", "sounds/knopka.mp3")
    video2_button = ImageButton(WIDTH / 2 - (252 / 2), 249, 175, 74, "1280x800", "data/back.png",
                              "data/back_border.png", "sounds/knopka.mp3")
    video3_button = ImageButton(WIDTH / 2 - (252 / 2), 323, 175, 74, "Full HD", "data/back.png",
                              "data/back_border.png", "sounds/knopka.mp3")
    video_back_button = ImageButton(WIDTH / 2 - (252 / 2), 397, 175, 74, "Назад", "data/back.png",
                              "data/back_border.png", "sounds/knopka.mp3")
    btn = [video1_button, video2_button, video3_button, video_back_button]
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background_image, (0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("VIDEO SETTINGS", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                fade()
                settings_menu()

            if event.type == pygame.USEREVENT and event.button == video1_button:
                print('НАЖАТА КНОПКА "video1_button"')
                change_video_mode(1068, 600)
                fade()
                running = False

            if event.type == pygame.USEREVENT and event.button == video2_button:
                print('НАЖАТА КНОПКА "video2_button"')
                change_video_mode(1424, 800)
                fade()
                running = False

            if event.type == pygame.USEREVENT and event.button == video3_button:
                print('НАЖАТА КНОПКА "video3_button (FULL HD)"')
                change_video_mode(1920, 1080, pygame.FULLSCREEN)
                fade()
                running = False

            if event.type == pygame.USEREVENT and event.button == video_back_button:
                print('НАЖАТА КНОПКА "video_back_button"')
                fade()
                settings_menu()

            for but in btn:
                but.handle_event(event)

        for but in btn:
            but.set_pos(WIDTH / 2 - (252 / 2))
            but.check_hover(pygame.mouse.get_pos())
            but.draw(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


def sound_settings():
    pass


def new_game():
    # Создание кнопок если понадобятся

    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("Добро пожаловать в игру!", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                fade()
                main_menu()

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


# Затемнение, переход между экранами
def fade():
    running = True
    fade_alpha = 0  #

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

        fade_alpha += 5
        if fade_alpha >= 105:
            fade_alpha = 255
            running = False

        pygame.display.flip()
        clock.tick(FPS)


main_menu()