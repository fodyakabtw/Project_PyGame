import time
import shutil
import pygame
import pygame.mixer
import sys
import os
from PIL import Image

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512, devicename=None)
pygame.init()
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
tree_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
rock_group = pygame.sprite.Group()
STEP = 50


def change_size(size, name):
    image = Image.open(name)
    image = image.resize(size)
    image.save(name)
    return name


# Воспомогательная функция воспроизведения звуков.
def sound_playback(file, volume=0.4, flagstoporpause=False):
    global gromkost
    volume = gromkost
    s = pygame.mixer.Sound(file)
    s.set_volume(volume)
    pygame.mixer.music.rewind()
    if flagstoporpause:
        s.stop()
    else:
        s.set_volume(volume)
        pygame.mixer.music.rewind()
        s.play()


SIZE = WIDTH, HEIGHT = 1280, 800
FPS = 60
level = []
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SIZE)
s = pygame.mixer.Sound('sounds/music_fon.wav')
s.set_volume(0.4)
s.play(loops=-1)
name = 'data/level1_copy.txt'
pygame.display.set_icon(pygame.image.load('data/icon.png'))
background_image = pygame.image.load(change_size(SIZE, 'data/background.png'))
pygame.display.set_caption('The Legend of a Kingdom')
# Загрузка и установка своего курсора
cursor = pygame.image.load("data/cursor.png")
pygame.mouse.set_visible(False)
gromkost = 1.0


def new_game():
    global name
    name = 'data/level1_copy.txt'
    shutil.copy('data/lvl1.txt', 'data/level1_copy.txt')
    shutil.copy('data/lvl2.txt', 'data/level2_copy.txt')
    game()


def record(n):
    global level
    with open(n, 'w') as f:
        for strk in level:
            f.writelines(''.join(strk) + '\n')


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением {fullname} не найден")
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


tile_images = {'wall': load_image('wall.png'), '.': load_image('grass.png'),
               'a': load_image('abroad.png'), '1': load_image('upper_left_corner.png'),
               '2': load_image('left_wall.png'), '3': load_image('lower_left_corner.png'),
               '4': load_image('bottom_wall.png'), '5': load_image('lower_right_corner.png'),
               '6': load_image('right_wall.png'), '7': load_image('upper_right_corner.png'),
               '8': load_image('top_wall.png'), 't': load_image('tree.png'),
               'w': load_image('up_path.png'), 'd': load_image('right_path.png'),
               'e': load_image('path_right_turn.png'), 'c': load_image('path_right_turn_s.png'),
               'q': load_image('path_turn_l.png'), 'z': load_image('path_turn.png'),
               'r': load_image('end_a_path.png'), 'y': load_image('end_d_path.png'),
               'f': load_image('end_s_path.png'), 'g': load_image('end_w_path.png'),
               'm': load_image('door_left.png'), 'n': load_image('door_right.png'),
               'p': load_image('rock.png')}
enemies_images = {'s': load_image('slime_idle.png')}
tile_width = tile_height = 200
move_up = [load_image('up/up1.png'), load_image('up/up2.png'), load_image('up/up3.png'),
           load_image('up/up4.png'), load_image('up/up5.png'), load_image('up/up6.png'),
           load_image('up/up7.png'), load_image('up/up8.png')]
move_left = [load_image('left/left1.png'), load_image('left/left2.png'),
             load_image('left/left3.png'), load_image('left/left4.png'),
             load_image('left/left5.png'), load_image('left/left6.png'),
             load_image('left/left7.png')]
move_right = [load_image('right/right1.png'), load_image('right/right2.png'),
              load_image('right/right3.png'), load_image('right/right4.png'),
              load_image('right/right5.png'), load_image('right/right6.png'),
              load_image('right/right7.png')]
move_down = [load_image('down/down1.png'), load_image('down/down2.png'),
             load_image('down/down3.png'), load_image('down/down4.png'),
             load_image('down/down5.png')]


def terminate():
    pygame.quit()
    sys.exit()


def load_level(file):
    file = f'{file}'
    with open(file, 'r') as f:
        map_level = list(map(str.strip, f.readlines()))
    max_width = max(map(len, map_level))
    return list(map(lambda x: x.ljust(max_width, '.'), map_level))


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, object):
        object.rect = object.rect.move(self.dx, self.dy)

    def update(self, target):
        self.dx = WIDTH // 2 - target.rect.x - target.rect.w // 2
        self.dy = HEIGHT // 2 - target.rect.y - target.rect.h // 2


camera = Camera()


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, enemy):
        super().__init__(all_sprites, enemies_group)
        self.frames = []
        self.columns = columns
        self.enemy = enemy
        self.attack = False
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.pos = x, y
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.attack and self.cur_frame == len(self.frames) - 1:
            self.frames = []
            if self.enemy == 'player':
                self.cut_sheet(load_image('idle.png'), 12, 1)
                self.rect = self.rect.move(self.pos)
                self.cur_frame = 0
                self.attack = False
            else:
                self.cut_sheet(load_image('slime_idle.png'), 5, 1)
                self.rect = self.rect.move(self.pos)
                self.cur_frame = 0
                self.attack = False
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pox_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pox_y
        self.mask = pygame.mask.from_surface(self.image)


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(wall_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pos_y
        self.mask = pygame.mask.from_surface(self.image)


class Tree(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tree_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pos_y
        self.mask = pygame.mask.from_surface(self.image)


class Door(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(door_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pos_y
        self.mask = pygame.mask.from_surface(self.image)


class Rock(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(rock_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pos_y
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = pygame.image.load("data/down/down1.png")
        self.pos_x, self.pos_y = tile_width * pos_x, tile_height * pos_y
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pos_y
        self.status = ''
        self.hero_image_number_up = 0
        self.hero_image_number_down = 0
        self.hero_image_number_right = 0
        self.hero_image_number_left = 0
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, x, y):
        # Сохраняем текущую позицию
        current_pos = self.pos_x, self.pos_y

        # Двигаем спрайт
        self.rect = self.rect.move(x, y)
        self.pos_x, self.pos_y = self.pos_x + x, self.pos_y + y

        # Проверяем столкновения с группой врагов
        enemy_collision = pygame.sprite.spritecollideany(self, enemies_group)
        if enemy_collision and pygame.sprite.collide_mask(self, enemy_collision):
            battle(self.pos_x // 200, self.pos_y // 200)

        # Проверяем столкновения с группой стен
        wall_collision = pygame.sprite.spritecollideany(self, wall_group)
        if wall_collision and pygame.sprite.collide_mask(self, wall_collision):
            # Если есть столкновение со стеной, возвращаемся на предыдущую позицию
            self.rect = self.rect.move(-x, -y)
            self.pos_x, self.pos_y = current_pos

        # Проверяем столкновения с группой дверей
        door_collision = pygame.sprite.spritecollideany(self, door_group)
        if door_collision and pygame.sprite.collide_mask(self, door_collision):
            # Если есть столкновение со стеной, возвращаемся на предыдущую позицию
            self.rect = self.rect.move(-x, -y)
            self.pos_x, self.pos_y = current_pos
            sound_playback('sounds/door .mp3', 0.4)
            print('Столкновение с дверью!')

        # Проверяем столкновения с группой стен
        if pygame.sprite.spritecollideany(self, wall_group):
            self.rect = self.rect.move(-x, -y)
            self.pos_x, self.pos_y = current_pos

        tree_collision = pygame.sprite.spritecollideany(self, tree_group)
        if tree_collision and pygame.sprite.collide_mask(self, tree_collision):
            # Если есть столкновение с деревом, возвращаемся на предыдущую позицию
            self.rect = self.rect.move(-x, -y)
            self.pos_x, self.pos_y = current_pos

        # Проверяем столкновения с группой камней
        rock_collision = pygame.sprite.spritecollideany(self, rock_group)
        if rock_collision and pygame.sprite.collide_mask(self, rock_collision):
            # Если есть столкновение со стеной, возвращаемся на предыдущую позицию
            self.rect = self.rect.move(-x, -y)
            self.pos_x, self.pos_y = current_pos

    def input(self):
        self.status = False
        key = pygame.key.get_pressed()
        if key[pygame.K_s]:
            self.move(0, 25)
            self.status = 'down'
        if key[pygame.K_w]:
            self.move(0, -25)
            self.status = 'up'
        if key[pygame.K_a]:
            self.move(-25, 0)
            self.status = 'left'
        if key[pygame.K_d]:
            self.move(25, 0)
            self.status = 'right'

    def get_status(self):
        return self.status

    def get_rect(self):
        return self.pos_x, self.pos_y

    def update(self, player_status):
        if self.hero_image_number_up > 6:
            self.hero_image_number_up = 0
        if self.hero_image_number_down >= 4:
            self.hero_image_number_down = 0
        if self.hero_image_number_right > 4:
            self.hero_image_number_right = 0
        if self.hero_image_number_left > 4:
            self.hero_image_number_left = 0

        if player_status == 'up':
            self.hero_image_number_up += 1
            self.image = move_up[self.hero_image_number_up % 7]
        elif player_status == 'down':
            self.hero_image_number_down += 1
            self.image = move_down[self.hero_image_number_down % 6]
        elif player_status == 'right':
            self.hero_image_number_right += 1
            self.image = move_right[self.hero_image_number_right % 6]
        elif player_status == 'left':
            self.hero_image_number_left += 1
            self.image = move_left[self.hero_image_number_left % 4]


def generate_level(level):
    new_player, x, y = None, None, None
    lvl = []
    for y in range(len(level)):
        s = []
        for x in range(len(level[y])):
            s.append(level[y][x])
            if level[y][x] in ['.', 'w', 'd', 'e', 'c', 'q', 'z', 'r', 'y', 'f', 'g']:
                Tile(level[y][x], x, y)
            elif level[y][x] == 's':
                Tile('.', x, y)
                AnimatedSprite(load_image('slime_idle.png'), 5, 1, tile_width * x,
                               tile_height * y, "slime")
            elif level[y][x] in ['n',  'm']:
                Door(level[y][x], x, y)
            elif level[y][x] == 'p':
                Tile('.', x, y)
                Rock(level[y][x], x, y)
            elif level[y][x] in ['a', '1', '2', '3', '4', '5', '6', '7', '8', 't']:
                if level[y][x] == 't':
                    Tile('.', x, y)
                    Tree(level[y][x], x, y)
                else:
                    Wall(level[y][x], x, y)
            elif level[y][x] == '@':
                Tile('.', x, y)
                new_player = Player(x, y)
        lvl.append(s)
    return new_player, x, y, lvl


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

    def set_pos(self, x, y=None):
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

    def handle_event(self, event):  # Отслеживание нажатия кнопки
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.sound:
                self.sound.play()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))


# Функция вывода любого текста на экран
def print_text(mess, x, y, font_color=(0, 0, 0), font_type='Arial Black', font_size=30):
    font_type = pygame.font.Font(None, font_size)
    text = font_type.render(mess, True, font_color)
    screen.blit(text, (x, y))


flag_enable_sound = False


# Функция паузы
def pause():
    global flag_enable_sound, gromkost
    paused = True
    # Создание кнопок:
    return_to_menu = ImageButton(WIDTH / 2 - (160 / 2), 200, 160, 160, "",
                                 "data/return_to_menu.png",
                                 "data/return_to_menu.png",
                                 "sounds/knopka.mp3")
    continue_play = ImageButton(WIDTH / 2 - (160 / 2), 200, 160, 160, "",
                                "data/continue.png",
                                "data/continue.png",
                                "sounds/knopka.mp3")
    enable_sound = ImageButton(WIDTH / 2 - (160 / 2), 200, 160, 160, "",
                               "data/enable_sound.png",
                               "data/enable_sound.png",
                               "sounds/knopka.mp3")
    reset_game = ImageButton(WIDTH / 2 - (160 / 2), 380, 160, 160, "",
                             "data/reset_game.png",
                             "data/reset_game.png",
                             "sounds/knopka.mp3")
    disable_sound = ImageButton(WIDTH / 2 - (160 / 2), 200, 160, 160, "",
                                "data/disable_sound.png",
                                "data/disable_sound.png",
                                "sounds/knopka.mp3")
    btn = [return_to_menu, continue_play]
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                fade()
                (wall_group.empty(), tiles_group.empty(), enemies_group.empty(),
                 player_group.empty(), tree_group.empty(), door_group.empty(),
                 rock_group.empty())
                main_menu()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                sound_playback('sounds/knopka.mp3', gromkost)
                fade()
                (wall_group.empty(), tiles_group.empty(), enemies_group.empty(),
                 player_group.empty(), tree_group.empty(), door_group.empty(),
                 rock_group.empty())
                main_menu()

                paused = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                sound_playback('sounds/knopka.mp3', gromkost)
                paused = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_3:
                sound_playback('sounds/knopka.mp3', gromkost)
                flag_enable_sound = not flag_enable_sound
                if flag_enable_sound:
                    s.stop()
                else:
                    s.play()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_4:
                (wall_group.empty(), tiles_group.empty(), enemies_group.empty(),
                 player_group.empty(), tree_group.empty(), door_group.empty(),
                 rock_group.empty())
                sound_playback('sounds/knopka.mp3', gromkost)
                fade()
                game()

            for but in btn:
                but.handle_event(event)
            reset_game.handle_event(event)

            if flag_enable_sound:
                disable_sound.handle_event(event)
            else:
                enable_sound.handle_event(event)

        i = -50 + WIDTH / 2 - 180
        for but in btn:
            but.set_pos(i)
            i += 180
            but.check_hover(pygame.mouse.get_pos())
            but.draw(screen)

        reset_game.set_pos(WIDTH / 2 - 50)
        reset_game.check_hover(pygame.mouse.get_pos())
        reset_game.draw(screen)

        if flag_enable_sound:
            disable_sound.set_pos(WIDTH / 2 + 130)
            disable_sound.check_hover(pygame.mouse.get_pos())
            disable_sound.draw(screen)
        else:
            enable_sound.set_pos(WIDTH / 2 + 130)
            enable_sound.check_hover(pygame.mouse.get_pos())
            enable_sound.draw(screen)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            paused = False

        pygame.display.update()
        clock.tick(15)


# Воспомогательная функция изменения разрешения окна игры.
def change_video_mode(w, h, fullscreen=0):
    global screen, SIZE, WIDTH, HEIGHT, background_image
    SIZE = WIDTH, HEIGHT = w, h
    screen = pygame.display.set_mode(SIZE, fullscreen)
    background_image = pygame.image.load(change_size(SIZE, 'data/background.png'))


# Функция основного меню игры:
def main_menu():
    # Кнопки
    new_game_button = ImageButton(WIDTH / 2 - (252 / 2), 175, 252, 75, "",
                                  "data/new_game.png",
                                  "data/new_game_hover.png",
                                  "sounds/knopka.mp3")
    play_button = ImageButton(WIDTH / 2 - (252 / 2), 250, 252, 75, "",
                              "data/start.png",
                              "data/start_hover.png",
                              "sounds/knopka.mp3")
    settings_button = ImageButton(WIDTH / 2 - (252 / 2), 325, 252, 74, "",
                                  "data/settings.png",
                                  "data/settings_hover.png",
                                  "sounds/knopka.mp3")
    store_button = ImageButton(WIDTH / 2 - (252 / 2), 400, 252, 74, "",
                               "data/store.png",
                               "data/store_hover.png",
                               "sounds/knopka.mp3")
    quit_button = ImageButton(WIDTH / 2 - (252 / 2), 475, 252, 74, "",
                              "data/quit.png",
                              "data/qui_hovert.png",
                              "sounds/knopka.mp3")
    game_name = ImageButton(WIDTH / 2 - (960 / 2), 0, 960, 150, "",
                            "data/game_name.png",
                            "data/game_name.png",
                            "sounds/knopka.mp3")
    # Добавление кнопок в список
    btn = [new_game_button, play_button, settings_button, store_button, quit_button]
    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.USEREVENT and event.button == new_game_button:
                fade()
                new_game()

            if event.type == pygame.USEREVENT and event.button == play_button:
                fade()
                game()

            if event.type == pygame.USEREVENT and event.button == settings_button:
                fade()
                settings_menu()

            if event.type == pygame.USEREVENT and event.button == store_button:
                print('В РАЗРАБОТКЕ!!!')

            if event.type == pygame.USEREVENT and event.button == quit_button:
                running = False
                pygame.quit()
                sys.exit()

            for but in btn:
                but.handle_event(event)

        for but in btn:
            but.set_pos(WIDTH / 2 - (252 / 2))
            but.check_hover(pygame.mouse.get_pos())
            but.draw(screen)
        game_name.set_pos(WIDTH / 2 - (960 / 2))
        game_name.draw(screen)

        # Отрисовка курсора в текущей позиции мыши !нужно делать в каждой фукнции перед флипом!
        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


def settings_menu():
    # Создание кнопок
    audio_button = ImageButton(WIDTH / 2 - (252 / 2), 175, 252, 74, "",
                               "data/sound.png",
                               "data/sound_hover.png",
                               "sounds/knopka.mp3")
    video_button = ImageButton(WIDTH / 2 - (252 / 2), 249, 252, 75, "",
                               "data/video.png",
                               "data/video_hover.png",
                               "sounds/knopka.mp3")
    back_button = ImageButton(WIDTH / 2 - (252 / 2), 324, 252, 75, "",
                              "data/back.png",
                              "data/back_hover.png",
                              "sounds/knopka.mp3")
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

            if event.type == pygame.USEREVENT and event.button == audio_button:
                sound_settings()
                fade()

            if event.type == pygame.USEREVENT and event.button == back_button:
                fade()
                main_menu()

            if event.type == pygame.USEREVENT and event.button == video_button:
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
    video1_button = ImageButton(WIDTH / 2 - (252 / 2), 175, 252, 74, "",
                                "data/960X600.png",
                                "data/960X600_hover.png",
                                "sounds/knopka.mp3")
    video2_button = ImageButton(WIDTH / 2 - (252 / 2), 249, 252, 74, "",
                                "data/1280X800.png",
                                "data/1280X800_hover.png",
                                "sounds/knopka.mp3")
    video3_button = ImageButton(WIDTH / 2 - (252 / 2), 323, 252, 74, "",
                                "data/fullhd.png",
                                "data/fullhd_hover.png",
                                "sounds/knopka.mp3")
    video_back_button = ImageButton(WIDTH / 2 - (252 / 2), 397, 252, 74,
                                    "",
                                    "data/back.png",
                                    "data/back_hover.png",
                                    "sounds/knopka.mp3")
    btn = [video1_button, video2_button, video3_button, video_back_button]
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background_image, (0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("", True, (255, 255, 255))
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
                change_video_mode(1068, 600)
                fade()
                running = False

            if event.type == pygame.USEREVENT and event.button == video2_button:
                change_video_mode(1424, 800)
                fade()
                running = False

            if event.type == pygame.USEREVENT and event.button == video3_button:
                change_video_mode(1920, 1080, pygame.FULLSCREEN)
                fade()
                running = False

            if event.type == pygame.USEREVENT and event.button == video_back_button:
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
    global gromkost
    # Создание кнопок громкости
    sound1_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                "data/sound_not_press.png",
                                "data/sound_press.png",
                                "sounds/knopka.mp3")
    sound2_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                "data/sound_not_press.png",
                                "data/sound_press.png",
                                "sounds/knopka.mp3")
    sound3_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                "data/sound_not_press.png",
                                "data/sound_press.png",
                                "sounds/knopka.mp3")
    sound4_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                "data/sound_not_press.png",
                                "data/sound_press.png",
                                "sounds/knopka.mp3")
    sound5_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                "data/sound_not_press.png",
                                "data/sound_press.png",
                                "sounds/knopka.mp3")
    sound6_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                "data/sound_not_press.png",
                                "data/sound_press.png",
                                "sounds/knopka.mp3")
    sound7_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                "data/sound_not_press.png",
                                "data/sound_press.png",
                                "sounds/knopka.mp3")
    sound8_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                "data/sound_not_press.png",
                                "data/sound_press.png",
                                "sounds/knopka.mp3")
    sound9_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                "data/sound_not_press.png",
                                "data/sound_press.png",
                                "sounds/knopka.mp3")
    sound10_button = ImageButton(WIDTH / 2 - (252 / 2), HEIGHT / 2, 20, 20, "",
                                 "data/sound_not_press.png",
                                 "data/sound_press.png",
                                 "sounds/knopka.mp3")
    music_button = load_image('music_button.png')
    btn_list = [sound1_button, sound2_button, sound3_button, sound4_button, sound5_button,
                sound6_button, sound7_button, sound8_button, sound9_button, sound10_button]

    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background_image, (0, 0))

        screen.blit(music_button, (0, HEIGHT / 2 - 25))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                fade()
                settings_menu()

            if event.type == pygame.USEREVENT and event.button == sound1_button:
                gromkost = 0.1
                s.set_volume(0.1)
            if event.type == pygame.USEREVENT and event.button == sound2_button:
                gromkost = 0.2
                s.set_volume(0.2)
            if event.type == pygame.USEREVENT and event.button == sound3_button:
                gromkost = 0.3
                s.set_volume(0.3)
            if event.type == pygame.USEREVENT and event.button == sound4_button:
                gromkost = 0.4
                s.set_volume(0.4)
            if event.type == pygame.USEREVENT and event.button == sound5_button:
                gromkost = 0.5
                s.set_volume(0.5)
            if event.type == pygame.USEREVENT and event.button == sound6_button:
                gromkost = 0.6
                s.set_volume(0.6)
            if event.type == pygame.USEREVENT and event.button == sound7_button:
                gromkost = 0.7
                s.set_volume(0.7)
            if event.type == pygame.USEREVENT and event.button == sound8_button:
                gromkost = 0.8
                s.set_volume(0.8)
            if event.type == pygame.USEREVENT and event.button == sound9_button:
                gromkost = 0.9
                s.set_volume(0.9)
            if event.type == pygame.USEREVENT and event.button == sound10_button:
                gromkost = 1.0
                s.set_volume(1.0)

            for but in btn_list:
                but.handle_event(event)
        i = 0 + music_button.get_width() + 10
        for but in btn_list:
            but.set_pos(i)
            i += 20
            but.check_hover(pygame.mouse.get_pos())
            but.draw(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()
        clock.tick(FPS)


def game():
    global level, name
    screen1 = pygame.display.set_mode((WIDTH, HEIGHT))
    if WIDTH == 1920 and HEIGHT == 1080:
        change_video_mode(1920, 1080, pygame.FULLSCREEN)
    else:
        change_video_mode(WIDTH, HEIGHT)
    player, level_x, level_y, lvl = generate_level(load_level(name))
    level = lvl
    running = True
    while running:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pause()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                (wall_group.empty(), tiles_group.empty(), enemies_group.empty(),
                 player_group.empty(), tree_group.empty(), door_group.empty(),
                 rock_group.empty())
                main_menu()
        player.input()
        player.update(player.get_status())
        camera.update(player)
        screen1.fill('black')
        for sprite in all_sprites:
            camera.apply(sprite)
        tiles_group.draw(screen1)
        wall_group.draw(screen1)
        tree_group.draw(screen1)
        door_group.draw(screen1)
        rock_group.draw(screen1)
        enemies_group.draw(screen1)
        enemies_group.update()
        player_group.draw(screen1)
        clock.tick(15)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


# Затемнение, переход между экранами.
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

        fade_alpha += 2
        if fade_alpha >= 105:
            fade_alpha = 255
            running = False

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()
        clock.tick(FPS)


def result(res):
    if not res:
        image = pygame.image.load('data/you_win!.png')
        x = 347
    else:
        image = pygame.image.load('data/you_died!.png')
        x = 330
    y = 57
    pos = (WIDTH / 2 - x / 2), (HEIGHT / 2 - y / 2)
    screen.blit(image, pos)
    pygame.display.flip()
    time.sleep(3)
    fade()
    (wall_group.empty(), tiles_group.empty(), enemies_group.empty(),
     player_group.empty(), tree_group.empty(), door_group.empty(),
     rock_group.empty())
    game()


class Fighter:
    def __init__(self, name, x, y, max_hp, strength, n1, n2):
        self.name = name
        self.pos = x, y
        self.max_hp = max_hp
        self.strength = strength
        self.update_time = pygame.time.get_ticks()
        self.hp = max_hp
        self.state = 0
        self.frames = []
        self.frame_ind = 0
        self.states = []

        # load idle images
        self.idle_w = []
        for i in range(1, n1 + 1):
            self.idle_w.append(load_image(f'{self.name}/idle/idle{i}.png'))
        self.states.append(self.idle_w)

        # load loss hp images
        self.hp_loss = []
        for i in range(1, n2 + 1):
            self.hp_loss.append(load_image(f'{self.name}/HP_loss/HP_loss{i}.png'))
        self.states.append(self.hp_loss)

        # different mobs attack differently, so we add them separately
        if self.name == 'cat':
            # load bow attack
            self.attack_bow = []
            for i in range(1, 6):
                self.attack_bow.append(load_image(f'{self.name}/bow_attack/attack_bow{i}.png'))
            self.states.append(self.attack_bow)

            # load sword attack
            self.attack_sword = []
            for i in range(1, 9):
                self.attack_sword.append(load_image(f'{self.name}/sword_attack'
                                                    f'/attack_sword{i}.png'))
            self.states.append(self.attack_sword)

        if self.name == 'slime':
            # load attack
            self.attack = []
            for i in range(1, 10):
                self.attack.append(load_image(f'{self.name}/slime_attack/slime_attack{i}.png'))
            self.states.append(self.attack)

        self.image = self.states[self.state][self.frame_ind]
        self.alive = True
        self.rect = self.image.get_rect()

    def draw(self):
        screen.blit(self.image, self.pos)

    def update(self):
        animation_cooldown = 100
        self.image = self.states[self.state][self.frame_ind]

        # has enough time passed since the last picture update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_ind += 1
        if self.frame_ind >= len(self.states[self.state]):
            self.idle()

    def idle(self):
        self.frame_ind = 0
        self.state = 0
        self.update_time = pygame.time.get_ticks()

    def attacka(self, mob, n):
        if n == 3:
            damage = self.strength[1]
        else:
            damage = self.strength[0]
        mob.hp -= damage
        if mob.hp <= 0:
            mob.alive = False
        else:
            # set attack animation
            self.frame_ind = 0
            self.state = n
            self.update_time = pygame.time.get_ticks()

        # set hp loss animation
        mob.frame_ind = 0
        mob.state = 1
        mob.update_time = pygame.time.get_ticks()


def update_mana(m):
    if m >= 6:
        mana = load_image("6mana.png")
    else:
        mana = load_image(f"{m}mana.png")
    return mana


def update_health(name, rotate, hp):
    if name.hp * 100 / name.max_hp > 80:
        if rotate:
            hp = load_image("100hp_rotate.png")
        else:
            hp = load_image("100hp.png")
    elif (name.hp / name.max_hp) * 100 > 60:
        if rotate:
            hp = load_image("80hp_rotate.png")
        else:
            hp = load_image("80hp.png")
    elif (name.hp / name.max_hp) * 100 > 40:
        if rotate:
            hp = load_image("60hp_rotate.png")
        else:
            hp = load_image("60hp.png")
    elif (name.hp / name.max_hp) * 100 > 20:
        if rotate:
            hp = load_image("40hp_rotate.png")
        else:
            hp = load_image("40hp.png")
    elif (name.hp / name.max_hp) * 100 > 0:
        if rotate:
            hp = load_image("20hp_rotate.png")
        else:
            hp = load_image("20hp.png")
    else:
        if rotate:
            hp = load_image("0hp_rotate.png")
        else:
            hp = load_image("0hp.png")
    return hp


def battle(posi_x, posi_y):
    global level
    run = True

    # pseudo buttons
    bow_img = load_image("bow.png")
    numbs = [load_image("one.png"), load_image("two.png")]
    health = load_image("100hp.png")
    mana = load_image("6mana.png")
    bow_btn = ImageButton(220, 40, 80, 80, "",
                          'data/bow.png')
    sword_img = load_image("sword.png")
    sword_btn = ImageButton(320, 40, 80, 80, "",
                            'data/sword.png')
    btns = [bow_btn, sword_btn]

    # health image
    health = load_image("100hp.png")
    health_enemy = load_image("100hp_rotate.png")

    # mana image
    mana = load_image("3mana.png")
    mana_score = 3

    # background image
    background = pygame.image.load(change_size(SIZE, 'data/battle_background.png'))

    current_fighter = 1
    action_cooldown = 0
    action_wait_time = 90

    # cat and mob
    cat = Fighter('cat', WIDTH / 2 - 200, HEIGHT / 2, 100, [5, 25], 12, 3)
    slime = Fighter('slime', WIDTH / 2, HEIGHT / 2 - 50, 50, [20], 5, 6)

    while run:
        # draw background
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            # bow attack
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                # player action
                if cat.alive:
                    if current_fighter == 1:
                        cat.attacka(slime, 2)
                        sound_playback('sounds/bow.mp3', 0.4)
                        current_fighter += 1
                        mana_score += 1
                        mana = update_mana(mana_score)
                        health_enemy = update_health(slime, True, health_enemy)
            # sword attack
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                # player action
                if cat.alive:
                    if current_fighter == 1 and mana_score > 2:
                        cat.attacka(slime, 3)
                        sound_playback('sounds/sword.mp3', 0.4)
                        current_fighter += 1
                        mana_score -= 3
                        mana = update_mana(mana_score)
                        health_enemy = update_health(slime, True, health_enemy)

        cat.update()
        cat.draw()

        slime.update()
        slime.draw()

        # enemy action
        if current_fighter == 2:
            if slime.alive:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    slime.attacka(cat, 2)
                    sound_playback('sounds/slime_attack .mp3', 0.4)
                    current_fighter -= 1
                    health = update_health(cat, False, health)
                    action_cooldown = 0
            else:
                run = False
                (wall_group.empty(), tiles_group.empty(), enemies_group.empty(),
                 player_group.empty(), tree_group.empty(), door_group.empty(),
                 rock_group.empty())
                for i in range(len(level)):
                    for j in range(len(level[i])):
                        if level[i][j] == '@':
                            level[i][j] = '.'
                if level[posi_y][posi_x] == 's':
                    level[posi_y][posi_x] = '@'
                else:
                    if level[posi_y + 1][posi_x] == 's':
                        level[posi_y + 1][posi_x] = '@'
                    elif level[posi_y][posi_x + 1] == 's':
                        level[posi_y][posi_x + 1] = '@'
                    elif level[posi_y + 1][posi_x + 1] == 's':
                        level[posi_y + 1][posi_x + 1] = '@'
                record('data/level1_copy.txt')
                fade()
                result(False)

        if not cat.alive:
            run = False
            fade()
            result(True)

        # draw mana and health
        screen.blit(health, (10, 40))
        screen.blit(mana, (10, 115))
        screen.blit(health_enemy, (WIDTH - health_enemy.get_width() - 10, 40))

        for btn in btns:
            btn.draw(screen)
        k = 0
        for element in numbs:
            screen.blit(element, (220 + k, 120))
            k += 100

        pygame.display.flip()

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))


main_menu()
