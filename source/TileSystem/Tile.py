class Tile:
	def __init__(self, x, y, tile_template):
		self.x = x
		self.y = y
		self.template = tile_template
		self.platforms = None
		self.no_left_walls = False
		self.no_right_walls = False
	
	def is_victory(self):
		return self.template.is_victory()
		
	def get_images(self, counter):
		return [self.template.get_image(counter)]
	
	def get_platforms(self):
		if self.platforms == None:
			self.platforms = self.template.get_platforms(self.x, self.y, self.no_left_walls, self.no_right_walls)
		return self.platforms
	
	def is_water(self):
		return self.template.water_modifier
	
	def is_ladder(self):
		return self.template.ladder_modifier
	
	def is_ouch(self):
		return self.template.ouch_modifier
	
	def is_kill(self):
		return self.template.kill_modifier
	
	def remove_walls(self, left):
		if left:
			self.no_left_walls = True
		else:
			self.no_right_walls = True
	
	def has_up_inclines(self):
		return self.template.has_up_inclines
	
	def has_down_inclines(self):
		return self.template.has_down_inclines
	
class CompositeTile:
	def __init__(self, x, y, tile_templates):
		self.physics_template = self.get_dominant_physics(tile_templates)
		self.templates = tile_templates
		self.platforms = None
		self.x = x
		self.y = y
		self.no_left_walls = False
		self.no_right_walls = False
	
	def is_victory(self):
		for template in self.templates:
			if template.is_victory():
				return True
		return False
		
	def remove_walls(self, left):
		if left:
			self.no_left_walls = True
		else:
			self.no_right_walls = True
	
	def get_images(self, counter):
		images = []
		for template in self.templates:
			images.append(template.get_image(counter))
		return images
	
	def get_platforms(self):
		if self.platforms == None:
			self.platforms = self.physics_template.get_platforms(self.x, self.y, self.no_left_walls, self.no_right_walls)
		return self.platforms
	
	def get_dominant_physics(self, tile_templates):
		self.water_modifier = False
		self.ladder_modifier = False
		self.kill_modifier = False
		self.ouch_modifier = False
		
		hierarchy = {
			'': 0,
			'passable': 1,
			'platform' : 2,
			'unpassable' : 3,
			'incline_up' : 4,
			'incline_down' : 5,
			'shallow_incline_up_upper' : 6,
			'shallow_incline_up_lower' : 7,
			'shallow_incline_down_upper' : 8,
			'shallow_incline_down_lower' : 9
			}
		
		physics = tile_templates[0]
		
		for i in range(1, len(tile_templates)):
			rank_a = hierarchy[self.filter_modifiers(physics.physics)]
			rank_b = hierarchy[self.filter_modifiers(tile_templates[i].physics)]
			if rank_b > rank_a:
				physics = tile_templates[i]
		return physics
	
	def has_up_inclines(self):
		return self.physics_template.has_up_inclines
	
	def has_down_inclines(self):
		return self.physics_template.has_down_inclines
	
	# will filter out the modifier tags and return just the physics	
	def filter_modifiers(self, raw_physics):
		
		final_physics = ''
		for physics in raw_physics.split('|'):
			if physics == 'water':
				self.water_modifier = True
			elif physics == 'ladder':
				self.ladder_modifier = True
			elif physics == 'kill':
				self.kill_modifier = True
			elif physics == 'ouch':
				self.ouch_modifier = True
			else:
				final_physics = physics
		return final_physics
	
	def is_water(self):
		return self.water_modifier
	
	def is_ladder(self):
		return self.ladder_modifier
	
	def is_ouch(self):
		return self.ouch_modifier
	
	def is_kill(self):
		return self.kill_modifier
	