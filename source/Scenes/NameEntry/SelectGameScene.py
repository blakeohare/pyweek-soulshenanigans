


class SelectGameScene:
	
	def __init__(self, starting_slot_index=0):
		games.initialize()
		self.next = self
		self.counter = 0
		self.cursor_index = starting_slot_index
		self.mode = 'selection' # 'copy' or 'erase' or paste
		self.text_entry = ''
		self.copy_from = 0
		wandStatus.wand_selected = 0
		
	def ProcessInput(self, events):
		
		enter_pressed = False
		
		for event in events:
			if event.down:
				if event.key == 'up':
					self.cursor_index -= 1
				elif event.key == 'down':
					self.cursor_index += 1
				elif event.key == 'start' or event.key == 'A' or event.key == 'B':
					enter_pressed = True
		if self.cursor_index < 0:
			self.cursor_index = 0
		elif self.cursor_index > 4:
			self.cursor_index = 4
		
		
		if enter_pressed:
			if self.cursor_index == 4:
				if self.mode == 'erase':
					self.mode = 'selection'
				else:
					self.mode = 'erase'
			elif self.cursor_index == 3:
				if self.mode == 'copy' or self.mode == 'paste':
					self.mode = 'selection'
				else:
					self.mode = 'copy'
			else: # 0, 1, 2
				if self.mode == 'selection':
					game = games.get_saved_game(self.cursor_index + 1)
					if game.get_value('saved') == 0:
						self.next = NameEntryScene(game, self.cursor_index)
					else:
						games.set_active_game(self.cursor_index + 1)
						game = games.active_game()
						if game.get_value('intro_shown') == 1:
							last_loc = game.get_value('last_location')
							if last_loc == None:
								last_loc = '1_1'
							last_loc = last_loc.split('_')
							world = int(last_loc[0])
							level = last_loc[1]
							nextScene = MapScene(world, level)
						else:
							jukebox.FadeOut(0.2)
							nextScene = CutSceneScene('intro', PlayScreen('0_1', 'a'))
						self.next = TransitionScene(self, nextScene, 'fadeout', 30)
				elif self.mode == 'erase':
					games.erase_game(self.cursor_index + 1)
					self.mode = 'selection'
				elif self.mode == 'copy':
					self.copy_from = self.cursor_index + 1
					self.mode = 'paste'
				elif self.mode == 'paste':
					if self.copy_from == self.cursor_index + 1:
						self.mode = 'copy'
					else:
						self.mode = 'selection'
						games.copy_game(self.copy_from, self.cursor_index + 1)
					
				
	
	def Render(self, screen):
		screen.fill((0,0,0))
		_selectGameBG.Render(screen)
		
		screen.blit(get_text('SELECT GAME'), (10, 10))
		
		x_offset = 10
		
		for slot in (1, 2, 3):
			game = games.get_saved_game(slot)
			is_empty = game.get_value('saved') == 0
			name = game.get_value('name')
			slot_label = get_text('SLOT ' + str(slot) + ': ')
			y = 30 + slot * 16
			mid_y = y + int(slot_label.get_height() / 2)
			
			screen.blit(slot_label, (x_offset, y))
			if is_empty:
				name = get_text('(Empty)')
			else:
				name = get_text(name)
			screen.blit(name, (x_offset + slot_label.get_width(), y))
			
			if self.cursor_index + 1 == slot:
				self._draw_cursor_at(x_offset - 5, mid_y)
				
			if self.mode == 'paste' and self.copy_from == slot:
				self._draw_cursor_at(x_offset - 5, mid_y, True)
		
		# copy game
		screen.blit(get_text('COPY GAME'), (x_offset, 120))
		if self.cursor_index == 3:
			self._draw_cursor_at(x_offset - 5, 120 + 4)
		
		# erase game
		screen.blit(get_text('ERASE GAME'), (x_offset, 140))
		if self.cursor_index == 4:
			self._draw_cursor_at(x_offset - 5, 140 + 4)
			
	def _draw_cursor_at(self, x, y, copy_from = False):
		color = (120, 120, 120)
		if copy_from:
			color = (128, 0, 128)
		elif self.mode == 'copy' or self.mode == 'paste':
			color = (0, 0, 255)
		elif self.mode == 'erase':
			color = (255, 0, 0)
		pygame.draw.circle(screen, color, (x, y), 3)
		
		
	def Update(self):
		self.counter += 1
		if self.counter == 1:
			jukebox.Stop()
		
class SelectGameBackground:
	def __init__(self):
		self.bg = pygame.Surface((256, 224))
		self.fake_playscreen = None
		self.bg.set_alpha(50)
	
	def Render(self, screen):
		if self.fake_playscreen == None:
			self.fake_playscreen = PlayScreen('1_1','a')
			self.fake_playscreen.renderInventory = False
			player = self.fake_playscreen.player
			player.y = -100
		self.fake_playscreen.Render(self.bg)
		return screen.blit(self.bg, (0, 0))
#STATIC

_selectGameBG = SelectGameBackground()