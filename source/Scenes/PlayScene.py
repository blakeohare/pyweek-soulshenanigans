
class PlayScreen:
	def __init__(self, level, screen, start_location=None):
		self.counter = 0
		self.render_counter = 0
		
		self.next = self
		self.g = 1.4
		
		self.level_id = level
		
		self.screen_id = screen
		
		self.level_info = levels.get_level(self.level_id + screen)
		
		wibbly_wobbly = False
		
		start_loc = self.level_info.get_start_location(start_location)
		
		self.target_vx = 0
		
		self.player = MainCharacter(start_loc[0] * 16, start_loc[1] * 16)
		self.enemies = self.level_info.get_enemies()
		self.mumblefoo = None
		self.wibblywobbly = WibblyWobblyRenderer()
		self.wibblywobbly_counter = 0
	
		self.allow_enemy_edit = True #TODO: change this to false right before release
		self.enemy_edit_mode = False
		self.wand_cooldown = 0
		self.bullets = []
	
	def get_sprites(self):
		
		sprites = []
		if self.mumblefoo != None:
			sprites.append(self.mumblefoo)
		sprites.append(self.player)
		sprites += self.enemies
		
		return sprites
	
	def get_camera_offset(self):
		width = self.level_info.get_width()
		height = self.level_info.get_height()
		x = self.player.x - 128
		y = self.player.y - 112
		x = max(min(x, width * 16 - 256), 0)
		y = max(min(y, height * 16 - 224), 0)
		return (x, y)
	
	def get_walls(self, x_left, x_right, y_top, y_bottom):
		tile_left = (x_left - 1) >> 4
		tile_right = (x_right + 1) >> 4
		tile_top = (y_top - 1) >> 4
		tile_bottom = (y_bottom + 1) >> 4
		
		platforms = []
		
		for tile_x in range(tile_left, tile_right + 1):
			for tile_y in range(tile_top, tile_bottom + 1):
				platforms += self.level_info.get_tile(tile_x, tile_y).get_platforms()['solid']
				
		return platforms
	
	def get_landing_surfaces(self, x, y_top, y_bottom):
		tile_left = (x - 1) >> 4
		tile_right = (x + 1) >> 4
		tile_top = (y_top - 1) >> 4
		tile_bottom = (y_bottom + 1) >> 4
		
		return self.level_info.get_landing_platforms_in_rectangle(tile_left - 1, tile_right + 1, tile_top, tile_bottom)
	
	def get_ceilings(self, x, y_top, y_bottom):
	
		tile_left = (x - 1) >> 4
		tile_right = (x + 1) >> 4
		tile_top = (y_top - 1) >> 4
		tile_bottom = (y_bottom + 1) >> 4
		
		return self.level_info.get_ceilings_in_rectangle(tile_left, tile_right, tile_top, tile_bottom)
	
	def get_just_inclines(self, x_left, x_right, y_top, y_bottom):
	
		tile_left = (x_left >> 4) - 1
		tile_right = (x_right >> 4) + 1
		tile_top = (y_top >> 4) - 1
		tile_bottom = (y_bottom >> 4) + 1
		
		return self.level_info.get_inclines_in_rectangle(tile_left, tile_right, tile_top, tile_bottom)
	
	def ProcessInput(self, events):
		for event in events:
			if event.key == 'start' and event.down:
				self.next = TransitionScene(self, PauseScene(self), 'fade', 10)
				jukebox.MakeQuiet()
			elif event.key == 'B':
				# jump
				if event.down and self.player.on_ground:
					self.player.vy = -15
					self.player.on_ground = False
					self.player.platform = None
				elif self.player.vy < 0:
					self.player.vy = 0
			elif event.key == 'Y' and event.down:
				if self.wand_cooldown <= 0 and len(self.bullets) < 5 and wandStatus.DepleteMagic():
					self.wand_cooldown = 5
					self.bullets.append(Bullet(self.player.left_facing, self.player.x, self.player.y, wandStatus.SelectedWand()))
		
		running = input.is_key_pressed('A')
		
		if input.is_key_pressed('left'):
			self.player.left_facing = True
			self.target_vx = (-3, -5)[running]
		elif input.is_key_pressed('right'):
			self.player.left_facing = False
			self.target_vx = (3, 5)[running]
		else:
			self.target_vx = 0
		
		if self.wand_cooldown > 0:
			self.target_vx = 0
		
		screechiness = 0.6 #TODO: make this dynamic for low-friction ice levels
		if self.target_vx != self.player.vx:
			if self.target_vx > self.player.vx:
				self.player.vx = min(self.target_vx, self.player.vx + screechiness)
			elif self.target_vx < self.player.vx:
				self.player.vx = max(self.target_vx, self.player.vx - screechiness)
	
	def Update(self):
		self.counter += 1
		
		self.wand_cooldown -= 1
		
		new_bullets = []
		camera_x = self.get_camera_offset()[0]
		
		for bullet in self.bullets:
			bullet.update()
			if not bullet.is_off_screen(camera_x, camera_x + 256):
				new_bullets.append(bullet)
		self.bullets = new_bullets
		
		if self.allow_enemy_edit:
			if _enemyEdit.ModeToggled():
				self.enemy_edit_mode = not self.enemy_edit_mode
				if not self.enemy_edit_mode:
					
					filename = 'levels' + os.sep + 'levels' + os.sep + self.level_id + self.screen_id + '.txt'
					c = open(filename, 'rt')
					lines = trim(c.read()).split('\n')
					output = ''
					for line in lines:
						parts = line.split(':')
						if not parts[0] == 'enemies':
							output += line + '\r\n'
					
					enemies = []
					for enemy in self.level_info.level_template.values['enemies']:
						enemies.append(enemy[0] + ',' + str(enemy[1]) + ',' + str(enemy[2]))
					if len(enemies) > 0:
						output += 'enemies:' + ' '.join(enemies) + '\r\n'
					c = open(filename, 'wt')
					c.write(trim(output))
					c.close()
					
					
			
			if self.enemy_edit_mode:
				num = _enemyEdit.NumPressed()
				if num >= 0:
					if num == 1:
						self.level_info.level_template.values['enemies'].append(('bat', int(self.player.x / 16), int(self.player.y / 16)))
						self.enemies = self.level_info.get_enemies()
						

		
		
		if self.counter == 1:
			jukebox.PlayLevelMusic('overworld1')
		
		for sprite in self.get_sprites():
			
			sprite.update(self)
			
			if self.player.special_state != None and self.player.special_state.block_update:
				continue
			
			sprite.dx = sprite.vx
			new_x = int(sprite.x + sprite.dx)
			
			if sprite.confined_to_scene:
				new_x = max(2, min(self.level_info.get_width() * 16 - 2, new_x))
			
			if sprite.dx > 0: #going right
				wall = self.find_leftmost_wall_in_path(sprite.x, new_x, sprite.get_head_bonk_top(), sprite.get_bottom())
				if wall != None:
					new_x = wall.get_left_wall_x() - 1
			elif sprite.dx < 0: #going left
				wall = self.find_rightmost_wall_in_path(new_x, sprite.x, sprite.get_head_bonk_top(), sprite.get_bottom())
				if wall != None:
					new_x = wall.get_right_wall_x() + 1
			
			# player may have possibly jumped through an incline
			if not sprite.on_ground and new_x != sprite.x:
				
				inclines = []
				
				sprite_bottom = sprite.get_bottom()
				
				for incline in self.get_just_inclines(min(new_x, sprite.x) - 2, max(new_x, sprite.x) + 2, sprite.y - 1, sprite.y + 1):
					
					#we're only interested in inclines in the horizontal component
					top = min(incline.y_left, incline.y_right)
					bottom = max(incline.y_left, incline.y_right)
					if sprite_bottom >= top and sprite_bottom <= bottom:
						#if new_x > sprite.x and incline.y_left > incline.y_right:
							inclines.append(incline)
						#elif new_x < sprite.x and incline.y_left < incline.y_right:
						#	inclines.append(incline)
				
				for incline in inclines:
				
					starts_above = sprite_bottom < incline.get_y_at_x(sprite.x)
					ends_above = sprite_bottom < incline.get_y_at_x(new_x)
					
					if starts_above and not ends_above:
						sprite.x = incline.get_x_at_y(sprite.y)
						
						#if incline.is_x_in_range(new_x):
						sprite.platform = incline
						sprite.on_ground = True
						sprite.vy = 0
						self.set_sprite_on_platform(sprite, incline)
						break
			
			sprite.x = new_x
			
			
			if not sprite.on_ground and not sprite.immune_to_gravity:
				sprite.vy += self.g
				sprite.vy = min(sprite.vy, 13)
			else:
				sprite.vy = 0
				
			sprite.dy = int(sprite.vy)
			
			new_y = sprite.y + sprite.dy
			
			if sprite.dy > 0:
				# sprite is falling
				
				y_offset = sprite.get_bottom() - sprite.y
				
				highest = self.find_highest_platform_in_path(sprite.x, sprite.y + y_offset, new_y + y_offset)
				
				if highest != None:
					sprite.on_ground = True
					sprite.platform = highest
					self.set_sprite_on_platform(sprite, highest)
				else:
					sprite.y = new_y
			elif sprite.dy <= 0 and sprite.platform == None:
				
				y_offset = sprite.get_head_bonk_top() - sprite.y
				
				lowest = self.find_lowest_platform_in_path(sprite.x, new_y + y_offset, sprite.y + y_offset)
				
				if lowest != None:
					sprite.dy = 0
					sprite.vy = 0
					new_y = lowest.get_bottom() + y_offset
					#TODO: play BONK noise
					
				else:
					sprite.y = new_y
			
			else:
				if sprite.platform != None:
					platform = sprite.platform
					if platform.is_x_in_range(sprite.x):
						self.set_sprite_on_platform(sprite, platform)
					else:
						# player walked off edge of platform
						
						new_platform_found = False
						
						# which way?
						if sprite.x < platform.left:
							# walked off left
							left = platform.left
							for left_platform in self.get_landing_surfaces(left - 1, sprite.y - 18, sprite.y + 18):
								
								# check to see if the right side of this platform is vertically aligned with 
								# the left side of the one you walked off
								if abs(left_platform.left + left_platform.width - platform.left) <= 1:
									
									# check to see if they're vertically aligned
									if abs(left_platform.y_right - platform.y_left) <= 1:
										sprite.platform = left_platform
										break
								
						else:
							# walked off right
							right = platform.left + platform.width
							for right_platform in self.get_landing_surfaces(right + 1, sprite.y - 18, sprite.y + 18):
								
								# check to see if the left side of this platform is vertically aligned with 
								# the right side of the one you walked off
								if abs(right_platform.left - (platform.left + platform.width)) <= 1:
									
									# check to see if they're vertically aligned
									if abs(right_platform.y_left - platform.y_right) <= 1:
										sprite.platform = right_platform
										break
						
						# if no new platform was found...
						if sprite.platform == platform:
							#the sprite has fallen off the edge
							sprite.on_ground = False
							sprite.platform = None
		
		if self.mumblefoo != None and self.mumblefoo.lifetime > 6:
			if self.is_collision(self.mumblefoo, self.player):
				self.mumblefoo = None
				# TODO: play noise
		
		if not self.enemy_edit_mode:
			if self.player.flashing_counter <= 0:
				for sprite in self.enemies:
					if self.is_collision(sprite, self.player):
						# You dropped the mumblefoo!
						self.player.flashing_counter = 60
						self.mumblefoo = SoulJar(self.player.x, self.player.y, self.counter)
		
		if self.mumblefoo == None:
			self.wibblywobbly_counter = max(0, self.wibblywobbly_counter - 5)
			
			# Check for door entry
			door = self.level_info.get_door_dest(int(self.player.x / 16), int(self.player.y / 16))
			if door != None and self.player.special_state == None:
				self.player.special_state = SpecialStateDoorEntry(door, self.player)
			
			# Check for victory
			victory_x = self.level_info.get_victory_x() * 16
			if victory_x > 0 and self.player.x >= victory_x:
				#TODO: automated victory sequence
				games.active_game().save_value('finished_world' + self.level_id, 1)
				games.active_game().save_to_file()
				parts = self.level_id.split('_')
				world = int(parts[0])
				level_from = int(parts[1][0])
				level_to = str(level_from + 1)
				level_from = str(level_from)
				if level_to == '6':
					level_to = 'next'
				self.next = MapScene(world, level_from, level_to)
			
		else:
			self.wibblywobbly_counter += 1
			if self.player.special_state == None and self.wibblywobbly_counter > self.wibblywobbly.get_max_severity():
				self.kill_player()
		
		if self.player.special_state == None and self.player.y > self.level_info.get_height() * 16 + 30:
			self.kill_player()
		
	
	def kill_player(self):
		self.player.special_state = SpecialStateDying(self.player)
		jukebox.PlayDeath()
	
	def is_collision(self, spriteA, spriteB):
		ra = spriteA.get_collision_radius() - 8
		rb = spriteB.get_collision_radius() - 8
		
		dx = spriteA.x - spriteB.x
		dy = spriteA.y - spriteB.y
		
		if (dx ** 2) + (dy ** 2) < (ra + rb) ** 2:
			return True
		return False
	
	def set_sprite_on_platform(self, sprite, platform):
		sprite.y = int(platform.get_y_at_x(sprite.x) - sprite.height + sprite.height / 2) # odd math to keep consistent rounding
	
	def find_leftmost_wall_in_path(self, left_x, right_x, y_top, y_bottom):
		return self._find_first_wall_in_path(left_x, right_x, y_top, y_bottom, True)
	
	def find_rightmost_wall_in_path(self, left_x, right_x, y_top, y_bottom):
		return self._find_first_wall_in_path(left_x, right_x, y_top, y_bottom, False)
	
	
	def _find_first_wall_in_path(self, left_x, right_x, y_top, y_bottom, going_right):
		furthest = None
		
		platforms = self.get_walls(left_x, right_x, y_top, y_bottom)
		
		for platform in platforms: # all platforms are guaranteed to be solid type
			if not (y_bottom <= platform.get_top() or y_top > platform.get_bottom()):
				if going_right:
					wall_x = platform.left
				else:
					wall_x = platform.left + platform.width
					
				if left_x <= wall_x and right_x >= wall_x:
					if furthest == None:
						furthest = platform
					elif going_right and furthest.left > platform.left:
						furthest = platform
					elif not going_right and furthest.left + furthest.width < platform.left + platform.width:
						furthest = platform
		return furthest
		
	def _find_first_platform_in_path(self, x, upper_y, lower_y, going_down):
		furthest = None
		
		if going_down:
			platforms = self.get_landing_surfaces(x, upper_y, lower_y)
		else:
			platforms = self.get_ceilings(x, upper_y, lower_y)
		
		for platform in platforms:
			if platform.is_x_in_range(x):
				if going_down:
					platform_y = platform.get_y_at_x(x)
				else:
					platform_y = platform.get_bottom()
					
				if upper_y <= platform_y and lower_y >= platform_y:
					if furthest == None:
						furthest = platform
					elif going_down and furthest.get_y_at_x(x) > platform_y:
						furthest = platform
					elif not going_down and furthest.get_bottom() < platform.get_bottom():
						furthest = platform
		
		return furthest
		
	def find_highest_platform_in_path(self, x, upper_y, lower_y):
		return self._find_first_platform_in_path(x, upper_y, lower_y, True)

	def find_lowest_platform_in_path(self, x, upper_y, lower_y):
		return self._find_first_platform_in_path(x, upper_y, lower_y, False)
		
	def Render(self, screen):
		
		self.render_counter += 1
		
		camera = self.get_camera_offset()
		cx = camera[0]
		cy = camera[1]
		
		bg = self.level_info.get_background_image()
		if bg != None:
			bg_percent = (0.0 + cx) / (self.level_info.get_width() * 16 - 256)
			bg_width = bg.get_width()
			
			bg_offset = -1 * bg_percent * (bg_width - 256)
			
			bg_offset += self.level_info.get_background_offset(self.render_counter)
			
			bg_offset = int(bg_offset % bg.get_width())
			screen.blit(bg, (bg_offset, 0))
			screen.blit(bg, (bg_offset - bg.get_width(), 0))
		
		col_start = max(0, int(cx / 16 - 1))
		col_end = min(self.level_info.get_width() - 1, col_start + 18)
		
		row_start = max(0, int(cy / 16 - 1))
		row_end = min(self.level_info.get_height() - 1, row_start + 16)
		
		for row in range(row_start, row_end + 1):
			for col in range(col_start, col_end + 1):
				x = col * 16
				y = row * 16
				tile = self.level_info.get_tile(col, row)
				imgs = tile.get_images(self.render_counter)
				if imgs != None:
					for img in imgs:
						if img != None:
							screen.blit(img, (x - cx, y - cy))
		
		if self.wibblywobbly_counter > 0:
			self.wibblywobbly.render_color_fade(screen, self.render_counter, self.wibblywobbly_counter)
		
		self.player.wand_cooldown= self.wand_cooldown
		
		for sprite in self.get_sprites():
			sprite.draw(screen, self.player.vx != 0, self.counter, camera)
		
		for bullet in self.bullets:
			bullet.draw(screen, cx, cy)
		
		if self.wibblywobbly_counter > 0:
			self.wibblywobbly.render(screen, self.render_counter, self.wibblywobbly_counter)

		self.render_status(screen)
		
		if self.enemy_edit_mode:
			label = get_text("(enemy insertion mode)")
			screen.blit(label, (0, 0))
	
	def render_status(self, screen):
		
		left = 256 - 10 - 100
		top = 5
		
		pygame.draw.rect(screen, (0, 0, 0), Rect(left - 1, top - 1, 102, 8))
		wand_width = wandStatus.GetMagic()
		colors = wandStatus.GetColors()
		pygame.draw.rect(screen, colors[0], Rect(left, top, wand_width, 5))
		pygame.draw.rect(screen, colors[1], Rect(left, top + 2, wand_width, 3))
		pygame.draw.rect(screen, colors[2], Rect(left, top + 4, wand_width, 2))
		
		
			

class EnemyEditInput:
	def __init__(self):
		self.num_pressed = -1
		self.toggle_mode = False
	
	def Clear(self):
		self.num_pressed = -1
		self.toggle_mode = False
		
	
	def Update(self, event):
		if event.type == KEYUP:
			if event.key in (K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0):
				self.num_pressed = event.key - K_0
			if event.key == K_e:
				self.toggle_mode = True
	def ModeToggled(self):
		return self.toggle_mode
	def NumPressed(self):
		return self.num_pressed
		
#STATIC
_enemyEdit = EnemyEditInput()