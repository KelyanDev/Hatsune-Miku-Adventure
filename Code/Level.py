import pygame
from support import import_csv_layout, import_cut_graphics
from Settings import tile_size, screen_width, screen_height
from Tiles import Tile, StaticTile
from Enemy import Enemy
from Decorations import Sky
from Player import Player
from Particle import ParticleEffect
from Game_Data import levels

class Level:
    def __init__(self,current_level,surface,create_overworld,change_health):
        # general setup
        self.display_surface = surface
        self.world_shift = 0

        # overworld connetion
        self.current_level = current_level
        level_data = levels[current_level]
        self.new_max_level = level_data['unlock']
        self.create_overworld = create_overworld

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout,change_health)
        
        # terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')

        # decorations setup
        decorations_layout = import_csv_layout(level_data['decorations'])
        self.decorations_sprites = self.create_tile_group(decorations_layout,'decorations')

        # pipes
        pipes_layout = import_csv_layout(level_data['pipes'])
        self.pipes_sprites = self.create_tile_group(pipes_layout,'pipes')
        
        # background terrain
        background_terrain_layout = import_csv_layout(level_data['bg_terrain'])
        self.background_terrain_sprites = self.create_tile_group(background_terrain_layout,'bg_terrain')

        # enemy
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout,'enemies')

        # constraint
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout,'constraint')

        # decoration
        self.sky = Sky()
        
        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # explosion particles
        self.explosion_sprite = pygame.sprite.Group()

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.create_overworld(self.current_level,0)

    def create_tile_group(self,layout,type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)

                    if type == 'decorations':
                        decorations_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
                        decoration_surface = decorations_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,decoration_surface)
                        
                    if type == 'pipes':
                        pipes_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
                        pipes_surface = pipes_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,pipes_surface)
                        
                    if type == 'bg_terrain':
                        bg_terrain_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
                        bg_surface = bg_terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,bg_surface)

                    if type == 'enemies':
                        sprite = Enemy(tile_size,x,y)

                    if type == 'constraint':
                        sprite = Tile(tile_size,x,y)

                    sprite_group.add(sprite)

        return sprite_group
    
    def player_setup(self,layout,change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x,y),self.display_surface,self.create_jump_particles,change_health)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load('../graphics/character/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size,x,y,hat_surface)
                    self.goal.add(sprite)
    
    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy,self.constraint_sprites,False):
                enemy.reverse()
        
    def create_jump_particles(self,pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,5)
        else:
            pos += pygame.math.Vector2(10,-5)
        jump_particle_sprite = ParticleEffect(pos,'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(-10,15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset,'land')
            self.dust_sprite.add(fall_dust_particle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        collidable_sprites = self.terrain_sprites.sprites() + self.pipes_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.terrain_sprites.sprites() + self.pipes_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
        
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0.1:
            player.on_ceiling = False

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level,0)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite,self.goal,False):
            self.create_overworld(self.current_level,self.new_max_level)

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite,self.enemy_sprites,False)

        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center= enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.player.sprite.direction.y = -8
                    explosion_sprite = ParticleEffect(enemy.rect.center,'explosion')
                    self.explosion_sprite.add(explosion_sprite)
                    enemy.kill()
                else:
                    self.player.sprite.get_damage()

    def run(self):
        # run the entire game / level

        # sky
        self.sky.draw(self.display_surface)
        
        # background terrain
        self.background_terrain_sprites.update(self.world_shift)
        self.background_terrain_sprites.draw(self.display_surface)

        # decorations
        self.decorations_sprites.update(self.world_shift)
        self.decorations_sprites.draw(self.display_surface)
        
        # terrain
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)
        
        # pipes
        self.pipes_sprites.update(self.world_shift)
        self.pipes_sprites.draw(self.display_surface)

        # enemy
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)
        self.explosion_sprite.update(self.world_shift)
        self.explosion_sprite.draw(self.display_surface)

        # dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # player sprite
        self.player.update()
        self.horizontal_movement_collision()

        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()

        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_death()
        self.check_win()
        self.input()

        self.check_enemy_collisions()