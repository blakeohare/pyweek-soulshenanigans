
class EnemySkeleton(Sprite):
	
	def __init__(self, x, y):
		self.lifetime = 0
		Sprite.__init__(self, x, y)
		self.width = 10
		self.height = 23
		self.left_facing = True
		
	def draw(self, surface, is_moving, counter, camera_offset):
		
		direction = ('Right', 'Left')[self.left_facing]
		
		file = direction + str(int(int(counter / 4) % 3)) + '.png'
		
		img = images.Get('sprites/Enemies/Skeleton/' + file)
		
		xy = self.get_top_left()
		x = xy[0] - camera_offset[0]
		y = xy[1] - camera_offset[1]
		
		surface.blit(img, (x, y))
	
	def update(self, playScene):
		self.lifetime += 1
		
		self.vx = (1, -1)[self.left_facing]
		if self.is_going_to_vx_bad(playScene):
			self.vx *= -1
			self.left_facing = not self.left_facing
	