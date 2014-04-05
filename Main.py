import pygame

print("hello world")

pygame.init()

WindowSurface = pygame.display.set_mode((640,480))

BlackColour = pygame.Color(0,0,0)
BlueColour = pygame.Color(0,0,255)

##pygame.draw.circle(WindowSurface,BlueColour,(300,50),20,0)

running = True

CircleCoord = (100,100)

while running:

    WindowSurface.fill(BlackColour)
    pygame.draw.circle(WindowSurface, BlueColour, CircleCoord, 20, 0)

    CircleCoord = (CircleCoord[0]+1,CircleCoord[1])

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False #close the window, foo
pygame.quit()
