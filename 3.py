# импорт нужных нам библиотек
import os
import pygame

# инициализация игрового цикла
pygame.init()

# установка размеров окна
size = width, height = 560, 670
screen = pygame.display.set_mode(size)

# установка названия окна
pygame.display.set_caption('Pacman')

# переменная, отвечающая за отображение очков
score = 0
dots_left = 243

# группы спрайтов
all_sprites = pygame.sprite.Group()
all_sprites2 = pygame.sprite.Group()
end_game_ = pygame.sprite.Group()

# переменные спрайтов и количества жизней игрока
life1 = pygame.sprite.Group()
life2 = pygame.sprite.Group()
life3 = pygame.sprite.Group()
lives = 3

pause = False
gameover = False
game_win = False


# функция загрузки изображения из локального хранилища
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)

    except pygame.error as message:

        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


# отображение спрайта лабиринта и его анимации при победе
class Lab(pygame.sprite.Sprite):
    image = load_image("lab.png")
    image2 = load_image("lab2.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Lab.image
        self.frame = 0
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    # анимация лабиринта при победе и переходе на след. уровень
    def update(self):
        if self.frame == 0:
            self.image = Lab.image
            self.frame = 1
        elif self.frame == 1:
            self.image = Lab.image2
            self.frame = 0


# следующие 3 класса - инициализация классов 3х спрайтов жизней для возможности
# скрывать их по очереди
class Life1(pygame.sprite.Sprite):
    image = load_image("life.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Life1.image
        self.rect = self.image.get_rect()
        self.rect.x = 390
        self.rect.y = 625


class Life2(pygame.sprite.Sprite):
    image = load_image("life.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Life2.image
        self.rect = self.image.get_rect()
        self.rect.x = 420
        self.rect.y = 625


class Life3(pygame.sprite.Sprite):
    image = load_image("life.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Life3.image
        self.rect = self.image.get_rect()
        self.rect.x = 450
        self.rect.y = 625


# следующие 4 класса снизу - инициализация коллайдеров стен всех 4х направлений
# которые при слиянии помогают определять не только столкновение, но и 
# направление стены, с которой произошло соприкосновение
class Up_Collider(pygame.sprite.Sprite):
    image = load_image("up_collider.png")

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Up_Collider.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 0
        self.rect.y = 0


class Down_Collider(pygame.sprite.Sprite):
    image = load_image("down_collider.png")

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Down_Collider.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 0
        self.rect.y = 0


class Left_Collider(pygame.sprite.Sprite):
    image = load_image("left_collider.png")

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Left_Collider.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 0
        self.rect.y = 0


class Right_Collider(pygame.sprite.Sprite):
    image = load_image("right_collider.png")

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Right_Collider.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 0
        self.rect.y = 0


# класс, отвечающий за все спрайтовые анимации в игре 
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites2)
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


# создаем класс Board
class Board:

    # конструктор класса
    def __init__(self, width1, height1):
        # ширина поля
        self.width = width1

        # высота поля
        self.height = height1

        # само игровое поле
        self.reload()

        # прочие характеристики (размер клетки, координаты)
        self.start = False
        self.left = 10
        self.top = 10
        self.cell_size = 20

    # исходная матрица лабиринта
    def reload(self):
        self.board = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1],
            [1, 6, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 6, 1, 1, 6, 2, 2, 2, 2, 2, 4,
             2, 2, 2, 2, 6, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2,
             1, 1, 1, 1, 2, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2,
             1, 1, 1, 1, 2, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2,
             1, 1, 1, 1, 2, 1],
            [1, 4, 2, 2, 2, 2, 4, 2, 2, 4, 2, 2, 4, 2, 2, 4, 2, 2, 4, 2, 2, 4,
             2, 2, 2, 2, 4, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2,
             1, 1, 1, 1, 2, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2,
             1, 1, 1, 1, 2, 1],
            [1, 6, 2, 2, 2, 2, 4, 1, 1, 6, 2, 2, 6, 1, 1, 6, 2, 2, 6, 1, 1, 4,
             2, 2, 2, 2, 6, 1],
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 2,
             1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 2,
             1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 2, 1, 1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 5, 1, 1, 2,
             1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2,
             1, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2,
             1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 4, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 4,
             0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2,
             1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2,
             1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 2, 1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 1, 2,
             1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2,
             1, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2,
             1, 1, 1, 1, 1, 1],
            [1, 6, 2, 2, 2, 2, 4, 2, 2, 4, 2, 2, 6, 1, 1, 6, 2, 2, 4, 2, 2, 2,
             2, 2, 2, 2, 6, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2,
             1, 1, 1, 1, 2, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2,
             1, 1, 1, 1, 2, 1],
            [1, 6, 2, 6, 1, 1, 4, 2, 2, 4, 2, 2, 4, 0, 0, 3, 2, 2, 4, 2, 2, 4,
             1, 1, 6, 2, 6, 1],
            [1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2,
             1, 1, 2, 1, 1, 1],
            [1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2,
             1, 1, 2, 1, 1, 1],
            [1, 6, 2, 4, 2, 2, 6, 1, 1, 6, 2, 2, 6, 1, 1, 6, 2, 2, 6, 1, 1, 6,
             2, 2, 4, 2, 6, 1],
            [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 2, 1],
            [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 2, 1],
            [1, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 2, 2, 4, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 6, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1]]

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # отображение точек (еды) на поле    
    def render(self, screen1):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == 2 or self.board[y][x] == 4 or \
                        self.board[y][x] == 6:
                    pygame.draw.rect(screen1, pygame.Color(253, 189, 150),
                                     (x * self.cell_size
                                      + self.cell_size // 2 - 3,
                                      y * self.cell_size
                                      + self.cell_size // 2 - 3, 6,
                                      6), 0)

    def get_cell_num(self, cell_num):
        return self.board[cell_num[0]][cell_num[1]]

    def get_cell(self, pos):
        if pos[0] // self.cell_size > self.width - 1 or \
                pos[1] // self.cell_size > self.height - 1:
            return None
        return pos[0] // self.cell_size, pos[1] // self.cell_size

    # функция начисления очков и съедания еды в лабиринте
    def scoring(self, pos):
        try:
            global score
            global dots_left
            if self.board[pos[1] //
                          self.cell_size][pos[0] // self.cell_size] == 2:
                self.board[pos[1]
                           // self.cell_size][pos[0] // self.cell_size] = 0
                score += 10
                dots_left -= 1
            if self.board[pos[1]
                          // self.cell_size][pos[0] // self.cell_size] == 4:
                self.board[pos[1]
                           // self.cell_size][pos[0] // self.cell_size] = 3
                score += 10
                dots_left -= 1
            if self.board[pos[1]
                          // self.cell_size][pos[0] // self.cell_size] == 6:
                self.board[pos[1]
                           // self.cell_size][pos[0] // self.cell_size] = 5
                score += 10
                dots_left -= 1
        except:
            pass


# класс призрака
class Blinky(AnimatedSprite):
    def __init__(self, sheet, columns, rows, x, y):
        self.frame = 0
        self.destination = 'right'
        self.next_dest = 'right'
        super().__init__(sheet, columns, rows, x, y)
        
    # обновление анимации призрака и зависимость её от направления его движения
    def update(self):
        if self.frame == 0:
            self.frame = 1
        else:
            self.frame = 0
        
        # проверка направления
        if self.destination == 'right':
            self.frame2 = self.frame
        elif self.destination == 'left':
            self.frame2 = self.frame + 2
        elif self.destination == 'up':
            self.frame2 = self.frame + 4
        elif self.destination == 'down':
            self.frame2 = self.frame + 6

        self.image = self.frames[self.frame2]
        self.mask = pygame.mask.from_surface(self.image)

    # функция, вычисляющяя кратчайшее расстояние по прямой до игрока
    def check(self):
        cell = board.get_cell(self.where())
        pac = pacman.where()
        # рассчитывание расстояния до игрока или запись большого числа в случае,
        # если рассматриваемая точка принадлежит стене
        if board.get_cell_num((cell[1], cell[0] + 1)) != 1:
            dist1 = (((cell[0] + 1) * 20 - pac[0]) ** 2 + (
                    cell[1] * 20 + 17 - pac[1]) ** 2) ** 0.5
        else:
            dist1 = 1000
        if board.get_cell_num((cell[1], cell[0] - 1)) != 1:
            dist2 = (((cell[0] - 1) * 20 - pac[0]) ** 2 + (
                    cell[1] * 20 + 17 - pac[1]) ** 2) ** 0.5
        else:
            dist2 = 1000
        if board.get_cell_num((cell[1] + 1, cell[0])) != 1:
            dist3 = ((cell[0] * 20 - pac[0]) ** 2 + (
                    (cell[1] + 1) * 20 + 17 - pac[1]) ** 2) ** 0.5
        else:
            dist3 = 1000
        if board.get_cell_num((cell[1] - 1, cell[0])) != 1:
            dist4 = ((cell[0] * 20 - pac[0]) ** 2 + (
                    (cell[1] - 1) * 20 + 17 - pac[1]) ** 2) ** 0.5
        else:
            dist4 = 1000
        
        # запись последующего направления, для более гибкого движения, подобно
        # игроку
        if dist1 == min(dist1, dist2, dist3, dist4):
            self.next_dest = 'right'
        elif dist2 == min(dist1, dist2, dist3, dist4):
            self.next_dest = 'left'
        elif dist3 == min(dist1, dist2, dist3, dist4):
            self.next_dest = 'down'
        elif dist4 == min(dist1, dist2, dist3, dist4):
            self.next_dest = 'up'

    def check2(self):
        # нахождение пути и смена направления на поворотах
        cell = board.get_cell(self.where())
        if board.get_cell_num(
                (cell[1], cell[0] + 1)) != 1 and self.destination != 'left':
            self.next_dest = 'right'
        elif board.get_cell_num(
                (cell[1], cell[0] - 1)) != 1 and self.destination != 'right':
            self.next_dest = 'left'
        elif board.get_cell_num(
                (cell[1] + 1, cell[0])) != 1 and self.destination != 'up':
            self.next_dest = 'down'
        elif board.get_cell_num(
                (cell[1] - 1, cell[0])) != 1 and self.destination != 'down':
            self.next_dest = 'up'
    
    # возврат положения призрака
    def where(self):
        return self.rect.x + 17, self.rect.y + 17

    # обнуление позиции и направления призрака, т.е возвращение его на старт
    def restart(self):
        self.rect.x = 264
        self.rect.y = 453.5
        self.frame = 0
        self.destination = 'right'
        self.next_dest = 'right'
        
    # реализация движения врага
    def move(self):
        global cell
        
        # изменение направления при несовпадении следующего направления
        if self.next_dest == 'up':
            if not pygame.sprite.collide_mask(self, down_collider):
                self.destination = self.next_dest
        elif self.next_dest == 'down':
            if not pygame.sprite.collide_mask(self, up_collider):
                self.destination = self.next_dest
        elif self.next_dest == 'right':
            if not pygame.sprite.collide_mask(self, left_collider):
                self.destination = self.next_dest
        elif self.next_dest == 'left':
            if not pygame.sprite.collide_mask(self, right_collider):
                self.destination = self.next_dest
        
        # само движение противника
        if self.destination == 'right':
            cell = board.get_cell(self.where())
            if not pygame.sprite.collide_mask(self, left_collider):
                self.rect = self.rect.move(1, 0)
        elif self.destination == 'left':
            cell = board.get_cell(self.where())
            if not pygame.sprite.collide_mask(self, right_collider):
                self.rect = self.rect.move(-1, 0)
        elif self.destination == 'up':
            cell = board.get_cell(self.where())
            if not pygame.sprite.collide_mask(self, down_collider):
                self.rect = self.rect.move(0, -1)
        elif self.destination == 'down':
            cell = board.get_cell(self.where())
            if not pygame.sprite.collide_mask(self, up_collider):
                self.rect = self.rect.move(0, 1)
        
        # проверка и изменение направления на поворотах
        if board.get_cell_num(
                (cell[1], cell[0])) == 4 or \
                board.get_cell_num((cell[1], cell[0])) == 3:
            blinky.check()
        elif board.get_cell_num(
                (cell[1], cell[0])) == 5 or \
                board.get_cell_num((cell[1], cell[0])) == 6:
            blinky.check2()


# класса Игрока
class Pacman(AnimatedSprite):

    # инициализация класса
    def __init__(self, sheet, columns, rows, x, y):
        self.angle = 0
        self.next_ang = 0
        super().__init__(sheet, columns, rows, x, y)

    # реализация движения Пакмана
    def move(self):

        # проверка на наличие нового направления, не совпадающего с нынешним
        if self.next_ang != self.angle:
            if self.next_ang == 90:
                if not pygame.sprite.collide_mask(self, down_collider):
                    self.angle = self.next_ang
            elif self.next_ang == -90:
                if not pygame.sprite.collide_mask(self, up_collider):
                    self.angle = self.next_ang
            elif self.next_ang == 0:
                if not pygame.sprite.collide_mask(self, left_collider):
                    self.angle = self.next_ang
            elif self.next_ang == 180:
                if not pygame.sprite.collide_mask(self, right_collider):
                    self.angle = self.next_ang
        
        # поворот игрока, изменение его направления и проверка 
        # на сталкивание со стенами
        if self.angle == 0:
            if not pygame.sprite.collide_mask(self, left_collider):
                self.rect = self.rect.move(1, 0)
            else:
                self.image = self.frames[1]
                self.image = pygame.transform.rotate(self.image, self.angle)

        elif self.angle == 180:
            if not pygame.sprite.collide_mask(self, right_collider):
                self.rect = self.rect.move(-1, 0)
            else:
                self.image = self.frames[1]
                self.image = pygame.transform.rotate(self.image, self.angle)

        elif self.angle == 90:
            if not pygame.sprite.collide_mask(self, down_collider):
                self.rect = self.rect.move(0, -1)
            else:
                self.image = self.frames[1]
                self.image = pygame.transform.rotate(self.image, self.angle)

        elif self.angle == -90:
            if not pygame.sprite.collide_mask(self, up_collider):
                self.rect = self.rect.move(0, 1)
            else:
                self.image = self.frames[1]
                self.image = pygame.transform.rotate(self.image, self.angle)
        
        # реализация "телепортации" игрока при движении в туннеле
        if self.rect.x < -34:
            self.rect.x = 561
        elif self.rect.x > 560:
            self.rect.x = -34

    # реализация запоминания следующего поворота для удобства управления
    def rot(self, angle):
        self.next_ang = angle

    # местоположение Пакмана
    def where(self):
        return self.rect.x + 17, self.rect.y + 17
    
    # возвращение игрока в начало игры и обнуление его направления
    def restart(self):
        self.rect.x = 294
        self.rect.y = 453.5
        self.angle = 0
        self.next_ang = 0

    # обновление анимации игрока
    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.mask = pygame.mask.from_surface(self.image)


# класс, отвечающий за анимацию смерти игрока
class End_Game(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(end_game_)
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

    # перемещение анимации смерти на последнюю позицию игрока
    def move(self, pos):
        self.rect.x = pos[0] - 17
        self.rect.y = pos[1] - 17

    # обновление анимации и её воспроизведение
    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)


# загрузка анимированных спрайтов
pacman = Pacman(load_image("pacman2.png"), 4, 1, 294, 453.5)
blinky = Blinky(load_image("blinky2.png"), 4, 2, 264, 453.5)
end_game = End_Game(load_image("end_game.png"), 9, 1, 264, 453.5)

# установка размеров доски
board = Board(28, 31)

# настройка коллайдеров
up_collider = Up_Collider()
down_collider = Down_Collider()
left_collider = Left_Collider()
right_collider = Right_Collider()

# отображение статичных (в большинстве своём) спрайтов
lab = Lab(all_sprites)
Life1(life1)
Life2(life2)
Life3(life3)

# устанавливаем FPS
fps = 140

# исходные счетчики
tick = 0
tick2 = 0
tick3 = 0

# начало отсчета времени
clock = pygame.time.Clock()

# начало игрового цикла
running = True

while running:
    # заливаем фон черным цветом
    screen.fill(pygame.Color("black"))

    # события игрового цикла
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # управление клавишами
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                pacman.rot(180)
            if event.key == pygame.K_RIGHT:
                pacman.rot(0)
            if event.key == pygame.K_UP:
                pacman.rot(90)
            if event.key == pygame.K_DOWN:
                pacman.rot(-90)
        
    # проверка счетчика
    if tick == 2:
        blinky.update()
        pacman.update()

    if abs(pacman.where()[0] - blinky.where()[0]) < 2 and abs(
            pacman.where()[1] - blinky.where()[1]) < 2:
        lives -= 1
        pause = True
        fps = 7
        end_game.move(pacman.where())
        pacman.restart()
        pygame.mixer.music.load(r'data\pacman_death.wav')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(0)
        blinky.restart()

    # движение игрока и призрака
    if not pause and not gameover and not game_win:
        pacman.move()
        if tick3 == 0:
            blinky.move()
        all_sprites2.draw(screen)
    elif pause and not gameover and not game_win:
        end_game_.draw(screen)
        end_game.update()
        tick2 += 1
        if tick2 == 9:
            pause = False
            tick2 = 0
            fps = 140
            if lives == -1:
                gameover = True
    elif pause and game_win and not gameover:
        lab.update()
        tick2 += 1
        if tick2 == 11:
            pause = False
            tick2 = 0
            fps = 140
            game_win = False
            pacman.restart()
            blinky.restart()
            board.reload()
    
    # вызываем метод спрайтов
    all_sprites.draw(screen)
    
    board.render(screen)
    board.scoring(pacman.where())

    # отправка координат игрока счётчику на проверку наличия точек в этом месте
    board.scoring(pacman.where())

    # вывод и настройка счётчика
    font = pygame.font.Font(None, 30)
    text = font.render(f"Score: {str(score)}", True, (0, 255, 0))
    text_x = 0
    text_y = 630
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x + 50, text_y))

    # проверка количества жизней
    if lives == 3:
        life1.draw(screen)
        life2.draw(screen)
        life3.draw(screen)
    elif lives == 2:
        life1.draw(screen)
        life2.draw(screen)
    elif lives == 1:
        life1.draw(screen)
    elif lives == -1 and gameover:
        # проигрыш игрока и всё, что должно при этом отобразиться
        pause = False
        pygame.draw.rect(screen, pygame.Color(0, 0, 0),
                         (220, 459, 135, 25), 0)
        font = pygame.font.Font(None, 35)
        text = font.render(f"Game Over", True, (255, 0, 0))
        text_x = 170
        text_y = 459
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x + 50, text_y))

    if dots_left == 0:
        # инициализация победы
        fps = 5
        pause = True
        game_win = True
        dots_left = 271

    # увеличение игровых счётчиков на 1 ед
    tick += 1
    tick3 += 1

    # обнуление счётчиков
    if tick > 4:
        tick = 0
    if tick3 > 1:
        tick3 = 0

    # стандартная функция времени игрового цикла
    clock.tick(fps)

    # обновление экрана
    pygame.display.flip()

# завершение игрового события
pygame.quit()
