# булька булька барабулька
import pygame
import random
import time


def start():
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Паровая машина в бегах!")
    # картинки
    start_button_img = pygame.image.load("data/start.png")
    # "рекорд"
    with open("data/record.txt", "r") as file:
        record_value = int(file.read())
    # тексто
    font = pygame.font.Font(None, 36)
    text1 = font.render("Рекорд: " + str(record_value), True, (0, 0, 0))
    text_rect1 = text1.get_rect(center=(screen_width / 2, 50))
    text2 = font.render("Управления по WASD, ESC = выход, R - перезапуск", True, (0, 0, 0))
    text_rect2 = text2.get_rect(center=(screen_width / 2, 100))

    # кнопка
    class Button(pygame.sprite.Sprite):
        def __init__(self, image, x, y):
            super().__init__()
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)

    # спрайты
    buttons = pygame.sprite.Group()
    start_button = Button(
        start_button_img, screen_width / 2 - start_button_img.get_width() / 2, 300
    )
    buttons.add(start_button)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.rect.collidepoint(event.pos):
                    return initialize()
        screen.fill(pygame.Color(255, 255, 224))
        screen.blit(text1, text_rect1)
        screen.blit(text2, text_rect2)
        buttons.draw(screen)
        pygame.display.flip()
    pygame.quit()


def initialize():
    class Maze:
        def __init__(
                self,
                min_solution_length,
                wall_possibility,  # возможность
                maze_size,  # размер
                start,  # первая координата
                player_start_coord,  # игрок старт
        ):
            self.size = maze_size
            self.wall_possibility = wall_possibility
            self.walls = []
            self.test_walls = ([])
            self.num_vertex = 1
            self.vertex_coord = []
            self.edge_list = []
            self.graphs = []
            self.start = start
            self.finish = 0
            self.min_solution_length = min_solution_length
            self.test_solution_length = 0
            self.test_solution_path = []
            self.solution_length = 0
            self.solution_path = []
            self.create_flag = False
            self.player_coord = (
                player_start_coord
            )
            self.player_cell = (
                    1 + self.player_coord[1] * self.size[0] + self.player_coord[0]
            )
            self.steps = 0
            self.weights = []
            self.amt_points = 0

        def coord2cell(self, coord):
            cell = 1 + coord[1] * self.size[0] + coord[0]
            return cell

        def randomus_wall(self):
            self.test_walls = []
            c = []
            for i in range(self.wall_possibility[0] * self.size[0] + 1):
                c.append(0)
            for i in range(self.wall_possibility[1] * self.size[1] + 1):
                c.append(1)
            self.test_walls.append(
                list(
                    random.sample(c, self.size[0] + 1) for _ in range(self.size[1] + 1)
                )
            )
            self.test_walls.append(
                list(
                    random.sample(c, self.size[0] + 1) for _ in range(self.size[1] + 1)
                )
            )
            for i in range(self.size[0] + 1):
                self.test_walls[0][0][self.size[0] - i] = 1
                self.test_walls[0][self.size[1]][self.size[0] - i] = 1
            for i in range(self.size[1] + 1):
                self.test_walls[0][i][self.size[0]] = 0
            for i in range(self.size[1] + 1):
                self.test_walls[1][i][0] = 1
                self.test_walls[1][i][self.size[0]] = 1
            for i in range(self.size[0] + 1):
                self.test_walls[1][0][i] = 0

        def get_edge_list(self):
            self.vertex_coord = self.celltocoord(self.num_vertex)
            self.edge_list = []

            for i in range(self.vertex_coord[1], self.size[0]):
                if self.test_walls[1][self.vertex_coord[0] + 1][i + 1]:
                    num = self.size[0] * self.vertex_coord[0] + i + 1
                    if num != self.num_vertex:
                        self.edge_list.append(num)
                    break
            for i in range(self.vertex_coord[1], -1, -1):
                if self.test_walls[1][self.vertex_coord[0] + 1][i]:
                    num = self.size[0] * self.vertex_coord[0] + i + 1
                    if num != self.num_vertex:
                        self.edge_list.append(num)
                    break
            for i in range(self.vertex_coord[0], self.size[1]):
                if self.test_walls[0][i + 1][self.vertex_coord[1]]:
                    num = self.size[0] * i + self.vertex_coord[1] + 1
                    if num != self.num_vertex:
                        self.edge_list.append(num)
                    break
            for i in range(self.vertex_coord[0], -1, -1):
                if self.test_walls[0][i][self.vertex_coord[1]]:
                    num = self.size[0] * i + self.vertex_coord[1] + 1
                    if num != self.num_vertex:
                        self.edge_list.append(num)
                    break
            self.edge_list.sort()

        def celltocoord(self, num_vertex):
            vertex_coord = []
            vertex_coord.append((num_vertex - 1) // self.size[0])
            vertex_coord.append((num_vertex - 1) % self.size[0])
            return vertex_coord

        def get_path(self):
            # кол-во вершин в графе
            n = self.size[0] * self.size[1]
            # список расстояний до вершин
            D = [None] * (n + 1)
            D[self.start] = 0  # расстояние до начальной вершины
            # список вершин для обхода
            Q = [self.start]
            Qstart = 0  # индекс начала списка
            # список предыдущих вершин
            Prev = [None] * (n + 1)
            # обход вершин графа, пока список не пуст
            while Qstart < len(Q):
                u = Q[Qstart]  # вершина
                Qstart += 1  # увеличивать индекс
                # обходить снежные вершины
                for v in self.graphs[u - 1]:
                    # расстояние до вершины не опред
                    if D[v] is None:
                        # новое расстояние
                        D[v] = D[u] + 1
                        Q.append(v)
                        Prev[v] = u
            self.amt_points = 0  # кол-во точек
            self.test_solution_length = 0
            self.test_solution_path = []
            for i in range(n + 1):
                Ans = []  # список для хранения пути до вершины i
                curr = i
                while curr is not None:
                    Ans.append(curr)  # текущая вершина в путь
                    curr = Prev[curr]
                # расстояне до вершины не нуль
                if D[i]:
                    self.amt_points += 1
                    if self.test_solution_length < D[i]:
                        # новая инфа
                        self.test_solution_length = D[i]
                        self.test_solution_path = Ans[::-1]
                        self.finish = i

        def try_create(self):
            self.create_flag = False
            self.graphs = (
                []
            )  # граф не создать
            self.randomus_wall()
            for i in range(
                    self.size[0] * self.size[1]
            ):
                self.num_vertex = i + 1
                self.get_edge_list()
                self.graphs.append(self.edge_list)  # добавить в графус
            self.get_path()
            if (
                    self.test_solution_length
                    > self.min_solution_length
            ):  # проверка возможности
                self.walls = self.test_walls.copy()
                self.solution_length = self.test_solution_length
                self.solution_path = self.test_solution_path.copy()
                self.create_flag = True

        def draw(
                self, color, coord, size, width_wall
        ):
            size_x = size[0] / self.size[0]
            size_y = size[1] / self.size[1]
            for i in range(self.size[1] + 1):
                for j in range(self.size[0] + 1):
                    if j + 1 < len(self.walls[0][i]):
                        if self.walls[0][i][j]:
                            pygame.draw.line(
                                screen,
                                color,
                                (
                                    int(j * size_x + coord[0]),
                                    int(i * size_y + coord[1]),
                                ),
                                (
                                    int((j + 1) * size_x + coord[0]),
                                    int(i * size_y + coord[1]),
                                ),
                                width_wall,
                            )
                    if i + 1 < len(self.walls[1]):
                        if self.walls[1][i + 1][j]:
                            pygame.draw.line(
                                screen,
                                color,
                                (
                                    int(j * size_x + coord[0]),
                                    int(i * size_y + coord[1]),
                                ),
                                (
                                    int(j * size_x + coord[0]),
                                    int((i + 1) * size_y + coord[1]),
                                ),
                                width_wall,
                            )

            crd = self.celltocoord(self.start)
            crd[0], crd[1] = crd[1], crd[0]
            crd[0] *= size_x
            crd[1] *= size_y
            pygame.draw.rect(
                screen,
                (230, 0, 0),
                (crd[0] + 10, crd[1] + 10, size_x - 15, size_y - 15),
            )
            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (crd[0] + 10, crd[1] + 10, size_x - 15, size_y - 15),
                5,
            )

            crd = self.celltocoord(self.finish)
            crd[0], crd[1] = crd[1], crd[0]
            crd[0] *= size_x
            crd[1] *= size_y
            pygame.draw.rect(
                screen,
                (0, 230, 0),
                (crd[0] + 10, crd[1] + 10, size_x - 15, size_y - 15),
            )
            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (crd[0] + 10, crd[1] + 10, size_x - 15, size_y - 15),
                5,
            )

        def wall_right(self):
            current_coords = self.player_coord
            vert_walls = self.walls[1][current_coords[1]]
            if vert_walls[current_coords[0]]:
                return True
            return False

        def wall_left(self):
            current_coords = self.player_coord
            vert_walls = self.walls[1][current_coords[1]]
            if vert_walls[current_coords[0] - 1]:
                return True
            return False

        def wall_up(self):
            current_coords = self.player_coord
            goriz_walls = self.walls[0][current_coords[1] - 1]
            if goriz_walls[current_coords[0] - 1]:
                return True
            return False

        def wall_down(self):
            current_coords = self.player_coord
            vert_walls = self.walls[0][current_coords[1]]
            if vert_walls[current_coords[0] - 1]:
                return True
            return False

        def player(self, size):
            self.player_cell = self.coord2cell(self.player_coord) - 9
            size_x = size[0] / self.size[0]
            size_y = size[1] / self.size[1]
            crd = self.celltocoord(self.player_cell)
            crd[0], crd[1] = crd[1], crd[0]
            crd[0] *= size_x
            crd[1] *= size_y
            pygame.draw.rect(
                screen,
                (230, 230, 230),
                (
                    crd[0] + 10,
                    crd[1] + 10,
                    size_x - 15,
                    size_y - 15,
                ),
            )
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (
                    crd[0] + 10,
                    crd[1] + 10,
                    size_x - 15,
                    size_y - 15,
                ),
                5,
            )

    pygame.init()
    pygame.font.init()
    size_screen = [325, 645]
    color_screen = (255, 255, 255)
    screen = pygame.display.set_mode(size_screen)
    pygame.display.set_caption("Паровая машина в бегах!")
    clock = pygame.time.Clock()
    FPS = 50
    keydown = []
    maze = Maze(20, [10, 1], [8, 16], 1, [1, 1])  #
    step = 1
    TMP_i = 0
    games_count = 0
    steps_player_count = 0
    default_time_per_step = 1.5
    time_elapsed = 0
    final_points = 0
    while step and games_count <= 5:
        keydown = pygame.key.get_pressed()
        if step == 1:
            maze.try_create()
            if maze.create_flag:
                TMP_i = 0
                step = 2
                points = 0
                if steps_player_count != 0:
                    points = (
                                                   (maze.min_solution_length * default_time_per_step)
                                                   / max(
                                               time_elapsed,
                                               (maze.min_solution_length * default_time_per_step),
                                           )
                                                   + maze.min_solution_length / steps_player_count
                                           ) * 50
                    if points >= 94:
                        points = 100
                    final_points += points
                games_count += 1
                steps_player_count = 0
                start_time = time.time()
            else:
                TMP_i += 1
        if step == 2:
            screen.fill(color_screen)
            maze.draw((0, 0, 0), [2, 2], [320, 640], 5)
            maze.player([320, 640])
            if keydown[pygame.K_r]:
                maze.player_coord = list(
                    map(lambda x: x + 1, maze.celltocoord(maze.start))
                )[::-1]
            if keydown[pygame.K_d]:
                moving = False
                while not maze.wall_right():
                    moving = True
                    maze.player_coord[0] += 1
                    screen.fill(color_screen)
                    maze.draw((0, 0, 0), [2, 2], [320, 640], 5)
                    maze.player([320, 640])
                    pygame.display.flip()
                    time.sleep(FPS * 0.001)
                if moving:
                    steps_player_count += 1
                if (
                        maze.player_coord
                        == list(map(lambda x: x + 1, maze.celltocoord(maze.finish)))[::-1]
                ):
                    maze.start = maze.finish
                    step = 1
                    end_time = time.time()
                    time_elapsed = end_time - start_time
            if keydown[pygame.K_a]:
                moving = False
                while not maze.wall_left():
                    moving = True
                    maze.player_coord[0] -= 1
                    screen.fill(color_screen)
                    maze.draw((0, 0, 0), [2, 2], [320, 640], 5)
                    maze.player([320, 640])
                    pygame.display.flip()
                    time.sleep(FPS * 0.001)
                if moving:
                    steps_player_count += 1
                if (
                        maze.player_coord
                        == list(map(lambda x: x + 1, maze.celltocoord(maze.finish)))[::-1]
                ):
                    maze.start = maze.finish
                    step = 1
                    end_time = time.time()
                    time_elapsed = end_time - start_time
            if keydown[pygame.K_w]:
                moving = False
                while not maze.wall_up():
                    moving = True
                    maze.player_coord[1] -= 1
                    screen.fill(color_screen)
                    maze.draw((0, 0, 0), [2, 2], [320, 640], 5)
                    maze.player([320, 640])
                    pygame.display.flip()
                    time.sleep(FPS * 0.001)
                if moving:
                    steps_player_count += 1
                if (
                        maze.player_coord
                        == list(map(lambda x: x + 1, maze.celltocoord(maze.finish)))[::-1]
                ):
                    maze.start = maze.finish
                    step = 1
                    end_time = time.time()
                    time_elapsed = end_time - start_time
            if keydown[pygame.K_s]:
                moving = False
                while not maze.wall_down():
                    moving = True
                    maze.player_coord[1] += 1
                    screen.fill(color_screen)
                    maze.draw((0, 0, 0), [2, 2], [320, 640], 5)
                    maze.player([320, 640])
                    pygame.display.flip()
                    time.sleep(FPS * 0.001)
                if moving:
                    steps_player_count += 1
                if (
                        maze.player_coord
                        == list(map(lambda x: x + 1, maze.celltocoord(maze.finish)))[::-1]
                ):
                    maze.start = maze.finish
                    step = 1
                    end_time = time.time()
                    time_elapsed = end_time - start_time
            pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                step = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    step = 0
        clock.tick()
    with open("data/record.txt", "r") as f:
        record_score = int(f.readlines()[0].strip())
    if round(final_points) > record_score:
        with open("data/record.txt", "w") as f:
            f.write(str(round(final_points)))
    return game_over(round(final_points))


def game_over(given_score):
    given_score = str(given_score)
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Паровая машина в бегах!")
    # кортинка новый игра
    new_img = pygame.image.load("data/new.png")
    # "рекорд"
    with open("data/record.txt", "r") as file:
        record_value = int(file.read())
    # тексто
    font = pygame.font.Font(None, 36)
    text = font.render("Рекорд: " + str(record_value), True, (0, 0, 0))
    score_text = font.render("Ваш счёт: " + given_score, True, (0, 0, 0))
    text_rect = text.get_rect(center=(screen_width / 2, 50))
    score = score_text.get_rect(center=(screen_width / 2, 100))

    # тыкалка
    class Button(pygame.sprite.Sprite):
        def __init__(self, image, x, y):
            super().__init__()
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)

    # спрайты
    buttons = pygame.sprite.Group()
    new_game_button = Button(
        new_img, screen_width / 2 - new_img.get_width() / 2, 300
    )
    buttons.add(new_game_button)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.rect.collidepoint(event.pos):
                    return True
        screen.fill(pygame.Color(255, 255, 224))
        screen.blit(text, text_rect)
        screen.blit(score_text, score)
        buttons.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    game_running = start()
    while game_running:
        initialize()
