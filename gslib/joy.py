import pygame

from gslib import character


def init_joys():
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        joystick.init()


def handle_joy(self, event):
    if event.type == pygame.JOYHATMOTION:
        x, y = event.value
        if x == -1:
            self.keys[pygame.K_LEFT] = True
        elif x == 1:
            self.keys[pygame.K_RIGHT] = True
        elif x == 0:
            self.keys[pygame.K_LEFT] = False
            self.keys[pygame.K_RIGHT] = False
        if y == -1:
            self.keys[pygame.K_DOWN] = True
        elif y == 1:
            self.keys[pygame.K_UP] = True
        elif y == 0:
            self.keys[pygame.K_DOWN] = False
            self.keys[pygame.K_UP] = False
    if event.type == pygame.JOYBUTTONDOWN:
        if event.button == 0:
            self.objects.append(character.Character(self, self.player1.coord[0], self.player1.coord[1], 16, 16,
                                                    character.gen_character()))
        elif event.button == 1:
            self.keys[pygame.K_ESCAPE] = True
        elif event.button == 2:
            self.options['FOV'] = False
        elif event.button == 3:
            self.options['VOF'] = True
    if event.type == pygame.JOYBUTTONUP:
        if event.button == 0:
            pass
        elif event.button == 1:
            self.keys[pygame.K_ESCAPE] = False
        elif event.button == 2:
            self.options['FOV'] = True
        elif event.button == 3:
            self.options['VOF'] = False
