from Settings import screen_width, screen_height
import pygame

class Sky:
    def __init__(self):
        # backgrounds
        self.last = pygame.image.load('../graphics/decoration/1.png')
        self.buildings = pygame.image.load('../graphics/decoration/2.png')
        self.houses = pygame.image.load('../graphics/decoration/3.png')
        self.first = pygame.image.load('../graphics/decoration/5.png')

        # stretch
        self.last = pygame.transform.scale(self.last,(screen_width,screen_height))
        self.buildings = pygame.transform.scale(self.buildings,(screen_width,screen_height))
        self.houses = pygame.transform.scale(self.houses,(screen_width,screen_height))
        self.first = pygame.transform.scale(self.first,(screen_width,screen_height))

    def draw(self,surface):
        surface.blit(self.last,(0,0))
        surface.blit(self.buildings,(0,0))
        surface.blit(self.houses,(0,0))
        surface.blit(self.first,(0,0))