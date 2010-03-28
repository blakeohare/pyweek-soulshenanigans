
pygame.init()

fullscreen = False

output_screen = pygame.display.set_mode((800, 600))

screen = pygame.Surface((256, 224))

counter = 0

# initialize joysticks connected at the time of startup
pygame.joystick.init()
for id in range(pygame.joystick.get_count()):
	joystick = pygame.joystick.Joystick(id)
	joystick.init()
	input.add_joystick(joystick)

scene = TitleScene()

while scene != None:
	
	start = time.time()
	
	events = []
	for event in pygame.event.get():
		if event.type == MUSICEND:
			soundtrack.HandleEvent(event)
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			scene = None
		elif event.type == KEYDOWN and event.key == K_f:
			fullscreen = not fullscreen
			if fullscreen:
				output_screen = pygame.display.set_mode((800, 600), FULLSCREEN)
			else:
				output_screen = pygame.display.set_mode((800, 600))
		else:
			events.append(event)
	
	if scene == None:
		break
	
	scene.ProcessInput(input.get_input(events))
	
	scene.Update()
	
	screen.fill((0,0,0))
	
	scene.Render(screen)
	
	pygame.transform.scale(screen, (800, 600), output_screen)
	
	if scene != scene.next:
		clear_text_cache()
		scene = scene.next
	
	end = time.time()
	
	ellapsed = end - start
	framerate = 1.0 / 30
	
	delay = framerate - ellapsed
	if delay > 0:
		time.sleep(delay)
	else:
		# remove me before release
		print('framerate dropping ('+str(counter)+')')
	pygame.display.flip()
	
	counter += 1

pygame.quit()