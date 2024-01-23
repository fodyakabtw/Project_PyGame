import pygame
import sys
import os


pygame.init()
size = width, height = 1000, 600
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
pygame.display.set_caption('The Legend of a Kingdom')


def pause():
    print("ПАУЗА")
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False

    pygame.display.update()
    clock.tick(15)


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


tile_images = {'wall': load_image('wall.png'), 'empty': load_image('grass.png'),
               'a': load_image('abroad.png'), '1': load_image('upper_left_corner.png'),
               '2': load_image('left_wall.png'), '3': load_image('lower_left_corner.png'),
               '4': load_image('bottom_wall.png'), '5': load_image('lower_right_corner.png'),
               '6': load_image('right_wall.png'), '7': load_image('upper_right_corner.png'),
               '8': load_image('top_wall.png'), 't': load_image('tree.png')}
player_image = load_image('cat.png')
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
    file = f'data/{file}'
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
        self.dx = width // 2 - target.rect.x - target.rect.w // 2
        self.dy = height // 2 - target.rect.y - target.rect.h // 2


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(enemies_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pox_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pox_y


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(wall_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pos_y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.pos_x, self.pos_y = tile_width * pos_x + 13, tile_height * pos_y + 5
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x + 13, tile_height * pos_y + 5
        self.status = ''
        self.hero_image_number_up = 0
        self.hero_image_number_down = 0
        self.hero_image_number_right = 0
        self.hero_image_number_left = 0

    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        self.pos_x, self.pos_y = self.pos_x + x, self.pos_y + y
        if (pygame.sprite.spritecollideany(self, wall_group) or
                pygame.sprite.spritecollideany(self, enemies_group)):
            self.rect = self.rect.move(-x, -y)
            self.pos_x, self.pos_y = self.pos_x - x, self.pos_y - y

    def input(self):
        player.status = False
        key = pygame.key.get_pressed()
        if key[pygame.K_s]:
            player.move(0, 25)
            player.status = 'down'
        if key[pygame.K_w]:
            player.move(0, -25)
            player.status = 'up'
        if key[pygame.K_a]:
            player.move(-25, 0)
            player.status = 'left'
        if key[pygame.K_d]:
            player.move(25, 0)
            player.status = 'right'

    def get_status(self):
        return self.status

    def get_rect(self):
        return self.pos_x, self.pos_y

    def update(self, player_status):
        if self.hero_image_number_up > 6:
            self.hero_image_number_up = 0
        if self.hero_image_number_down >= 4:
            self.hero_image_number_down = 0
        if self.hero_image_number_right > 5:
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
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == 's':
                Tile('empty', x, y)
                AnimatedSprite(load_image('slime_idle.png'), 5, 1, tile_width * x,
                               tile_height * y)
            elif level[y][x] in ['a', '1', '2', '3', '4', '5', '6', '7', '8', 't']:
                Wall(level[y][x], x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


all_sprites = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
camera = Camera()
player, level_x, level_y = generate_level(load_level('lvl1.txt'))
STEP = 50


def game():
    running = True

    while running:
        status1 = player.get_status()
        rect1 = player.get_rect()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause()
        player.input()
        player.update(player.get_status())
        camera.update(player)
        screen.fill('black')
        status2 = player.get_status()
        rect2 = player.get_rect()
        if status1 != status2 and rect1 != rect2:
            print(1)
        for sprite in all_sprites:
            camera.apply(sprite)
        wall_group.draw(screen)
        tiles_group.draw(screen)
        enemies_group.draw(screen)
        enemies_group.update()
        player_group.draw(screen)
        clock.tick(15)
        pygame.display.flip()


game()