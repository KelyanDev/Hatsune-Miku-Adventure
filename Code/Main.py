import pygame, sys
from Settings import *
from Level import Level
from Overworld import Overworld
from Ui import UI

class Game:
    def __init__(self):

        # game attributes
        self.max_level = 0
        self.max_health = 30
        self.cur_health = 30

        # overworld creation
        self.overworld = Overworld(0,self.max_level,screen,self.create_level)
        self.status = 'overworld'

        # user interface
        self.ui = UI(screen)

    def create_level(self,current_level):
        self.level = Level(current_level,screen,self.create_overworld,self.change_health)
        self.status = 'level'

    def create_overworld(self,current_level,new_max_level):
        if new_max_level > self.max_level and self.max_level != 3:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level,self.max_level,screen,self.create_level)
        self.status = 'overworld'

    def change_health(self,amount):
        if self.cur_health != 0:
            self.cur_health += amount

    def check_game_over(self):
        if self.cur_health <= 0:
            self.cur_health = self.max_health
            self.max_level = 0
            self.overworld = Overworld(0,self.max_level,screen,self.create_level)
            self.status = 'overworld'

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(self.cur_health,self.max_health)
            self.check_game_over()

pygame.init()
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((150,150,150))
    game.run()

    pygame.display.update()
    clock.tick(30)