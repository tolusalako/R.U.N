from gameobject import Object
import gamewindow
from os import listdir
import Tkinter as TK
from PIL import ImageTk, ImageFilter
from datetime import datetime
import sys, Queue
from collections import defaultdict
import time

controls = {
	'top' : '0x58',
	'right': '0x27',
	'left': '0x25',
	'topleft':'0x25\n0x58',
	'topright': '0x27\n0x58'
}



class Tile(tuple):
	def __init__(self, location, top = None, left = None, right = None, topright = None, topleft = None,
		score = 0, cost = 0):
		tuple.__init__(location)
		self.top = top
		self.left = left
		self.right = right
		self.topleft = topleft
		self.topright = topright
		self.score = score #from this to goal
		#self.cost = cost #from current to this
		self.is_goal = False
		self.direction = defaultdict(str)
		self.x = self.__getitem__(0)
		self.y = self.__getitem__(1)

	def children(self):
		result = []
		if not self.right is None:
			result.append(self.right)
			self.direction[self.right] = 'right'
		if not self.top is None:
			result.append(self.top)
			self.direction[self.top] = 'top'
		if not self.left is None:
			result.append(self.left)
			self.direction[self.left] = 'left'
		if not self.topleft is None:
			result.append(self.topleft)
			self.direction[self.topleft] = 'topleft'
		if not self.topright is None:
			result.append(self.topright)
			self.direction[self.topright] = 'topright'
		return result

	def cost(self, current): #Provides cost from current to this
		return abs(self.x - current.x)
			
#http://www.redblobgames.com/pathfinding/a-star/implementation.html
def a_star_search(start):
	frontier = Queue.PriorityQueue()
	frontier.put(start, 0)

   	came_from = {}
   	cost_so_far = {}
	came_from[start] = None
	cost_so_far[start] = 0
	found_goal = None
	path = []

	while not frontier.empty():
	    current = frontier.get()
	    
	    if current.is_goal:
			found_goal = current
			break
	    for next in current.children():
	        new_cost = cost_so_far[current] + next.cost(current)
	        if next not in cost_so_far or new_cost < cost_so_far[next]:
	            cost_so_far[next] = new_cost
	            priority = new_cost + next.score
	            frontier.put(next, priority)
	            came_from[next] = current
	            path.append(current.direction[next])

	#return came_from, cost_so_far, found_goal
	return path




class Park():
	def __init__(self, name, main_character):
		self.template_path = "template/";
		self.objects = [f for f in listdir(self.template_path)]
		title = name
		source = 0;
		self.threshold = .7
		self.status = defaultdict(str) #key = location, value = object_name
		self.destroy = False
		self.main_char= main_character
		self.char_location = None
		self.tile_size = (33, 33)
		self.current_tree = defaultdict(int) #key = location, value = Tile

		self.window = gamewindow.GameWindow(name, self.template_path)
		for i in range(len(self.window.source_list[0])):
			if title in self.window.source_list[1][i].lower():
				source = self.window.source_list[0][i]
				break;
		self.window.set_source(source)
		self.width, self.height = self.window.size()
		self.setup()


	def setup(self):
		self.downsize = 1
		self.max_x = self.window.size()[0]/self.tile_size[0]
		self.max_y = self.window.size()[1]/self.tile_size[1]
		self.generate_tiles()

		self.master = TK.Tk()
		self.base = TK.Frame(self.master)
		#self.master.protocol('WM_DELETE_WINDOW', self.__on_exit_preview)
		self.master.wm_title("RunAI")
		#self.master.iconbitmap('icon.ico')
		self.canvas = TK.Canvas(master = self.base, background = "#FFFFFF", height = self.height*self.downsize,
		 width = self.width*self.downsize)
		self.canvas.grid(row = 0, column = 0, sticky = TK.W)

		self.save_btn = TK.Button(master = self.base, text = 'Save', command = self.save_temp)
		self.save_btn.grid(row = 1, columnspan = 20, sticky = TK.W + TK.E)

		self.base.pack()
		#self.preview_loop()
		#self.hud_preview()
		self.update_status()
		self.tree_preview()
		#self.print_status()
		self.master.withdraw()
		self.master.mainloop()

	def update_status(self):
		self.temp_img = self.window.capture()
		if not self.temp_img is None:
			self.found_objects = gamewindow.find_objects_as_objects(self.temp_img, 
				[self.template_path + o for o in self.objects], self.threshold)
			self.status = defaultdict(str)
			for o in self.found_objects:
				t = self.get_tile(o.location)
				if not t is None:
					self.status[t] = o.name
					if o.name == self.main_char:
						self.char_location = t
			self.master.after(1, self.update_status)

	def generate_tree(self, root, direction, steps = 1, score = 1, cost = 1, set_last_step_to_goal = False):
		steps -= 1
		result = self.get_tile_in_direction(root, direction)
		max_jump = 4
		if not result is None:
			took_detour = False
			detour = None
			if self.status[result] == 'goomba' or self.status[result] == 'block':
				detour = self.get_tile_in_direction(result, 'top')
				while self.status[detour] == 'block' and max_jump > 0:
					if detour == None:
						pass

					took_detour = True
			score = cost * abs((result[0]- self.max_x) + (result[1] - self.max_y)) #http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html#S7
			if self.current_tree[result] != 0:
				for t in self.current_tree.keys():
					if t == result:
						result = t
			result.score = score
			exec('root.'+direction+'= result')
			self.current_tree[result] = score
			if steps > 0:
				self.generate_tree(result, direction, steps, score, cost + 1, set_last_step_to_goal)
				if took_detour:
					if direction == 'right' or direction == 'left':
						exec('root.top'+direction+'= detour')
						exec('root.'+direction+'= None')
						exec('detour.'+direction+'= result.'+direction)
						self.current_tree[result] = 0
						self.current_tree[detour] = score

			else:
				result.is_goal = True if set_last_step_to_goal else False
		else:
			root.is_goal = True if set_last_step_to_goal else False

	def check_forward_for_obstacles(self, root, steps = 4): #returns heighest height of obstacle or longest width of pit
		x, y = root
		w, h = self.tile_size
		heighest = 0
		pit_length = 0
		for i in xrange(w,steps*w, w):
			front = self.get_tile((x+i, y))
			if front is None: #Out of bounds or No obstacle.
				pass
			else:
				s = self.status[front]
				if s == 'goomba':
					heighest = max(heighest, 1)
				elif s == 'block':
					height = 1
					for j in xrange(h,steps*h, h):
						above = self.get_tile((x+i, y - j))
						if above is None:
							break
						elif self.status[above] == 'block':
							height += 1
					heighest = max(heighest, height)
				elif s == 'pipe':
					height = 4
				else: #If front is clear, check below it for pit
					below = self.get_tile((x+i, y+w))
					if below is not None and self.status[below] == '': #PIT!
						pit_length += 1
		return heighest, pit_length


	def get_tile_in_direction(self, start, direction):
		x,y = start
		w,h = self.tile_size
		return{
			'right' : self.get_tile((x + w, y)),
			'left' : self.get_tile((x - w, y)),
			'top' : self.get_tile((x, y - h)),
			'down' : self.get_tile((x, y + h)),
			'topleft' : self.get_tile((x - w, y - h)),
			'topright' : self.get_tile((x + w, y - h))
		}.get(direction, 'right') #Default

	def get_tile(self, size):
		w, h = self.tile_size
		x, y = size
		result = None
		try:
			result = Tile(self.tiles[y/h][x/w]) #New object
		except(Exception):
			pass
		return result

	def print_status(self):
		status = self.status
		for s in status.keys():
			print str(s) + ': ' + status[s]
		sys.stdout.flush()
		self.master.after(3000, self.print_status)

	def generate_tiles(self):
		self.tiles = []
		width, height = self.window.size()
		w, h = self.tile_size
		for row in range(0, height, h):
			R = []
			for col in range(0, width, w):
				R.append(Tile((col, row)))
			self.tiles.append(R)

	def save_temp(self):
		self.temp_img.save(str(datetime.now().strftime("%I-%M %p")) + '.png')

	def __on_exit_preview(self):
		self.destroy = True

	def preview_loop(self):
		self.temp_img = self.window.capture()
		if not self.temp_img is None:
			labels = ('mario', 'goomba', 'pickup')
			self.found_objects = gamewindow.find_objects_as_image(self.temp_img, [self.template_path + o for o in self.objects], self.threshold, write_labels = True, labels = labels)
			self.photo_preview = self.found_objects.copy()
			self.photo_preview = ImageTk.PhotoImage(self.found_objects.resize((int(self.width*self.downsize), int(self.height*self.downsize))))
			self.canvas.create_image((0, 0), image = self.photo_preview, anchor = TK.N +TK.W)
			self.master.after(1, self.preview_loop)


	def hud_preview(self):
		self.temp_img = self.window.capture()
		if not self.temp_img is None:
			self.found_objects = gamewindow.find_objects_as_objects(self.temp_img, [self.template_path + o for o in self.objects], self.threshold)
			self.canvas.delete(TK.ALL)
			for o in self.found_objects:
				color = ''
				if o.name == 'mario':
					color = 'blue'
				elif o.name == 'block':
					color = 'black'
				elif o.name == 'pickup':
					color = 'green'
				else:
					color = 'red'

				#w,h = o.size
				#start = o.location
				w,h = self.tile_size
				start = self.get_tile(o.location)
				end = start[0] + w, start[1]+h
				self.canvas.create_rectangle(start, end, fill = color)
			self.master.after(1, self.hud_preview)

	def tree_preview(self):
		self.current_tree.clear() #clear
		status = self.status.items()
		root = None
		for k,v in status:
			if v == 'mario':
				root = k
				break


		if root is not None:
			obstacle, pit = self.check_forward_for_obstacles(root, steps = 3)
			KEY_PRESS = 0.3
			KEY_PRESS_SMALL = 0.1
			if pit == obstacle == 0:
				self.window.pressKey(int(controls['right'], 0), KEY_PRESS)
			elif 0 < pit < 3:
				self.window.pressKey(int(controls['right'], 0), (pit*KEY_PRESS)/ 2)
				self.window.pressKey(int(controls['top'], 0), pit*KEY_PRESS_SMALL)
			else:
				self.window.pressKey(int(controls['top'], 0), obstacle*KEY_PRESS)
				self.window.pressKey(int(controls['right'], 0), KEY_PRESS)
			print obstacle, pit
			sys.stdout.flush()

		# 		self.current_tree[k] = -1
		# 		#self.generate_tree(k, 'left', 2, cost = 1)
		# 		# self.generate_tree(k, 'topleft', 4, cost = 1)
		# 		self.generate_tree(k, 'right', 5, cost = 1, set_last_step_to_goal = True)
		# 		# self.generate_tree(k, 'topright', 3, cost = 1)
		# 		# self.generate_tree(k, 'top', 3, cost = 1)

		# if root is not None:
		# 	result = a_star_search(root)
		# 	# print result[0]
		# 	# print
		# 	# print result[1]
		# 	# print root
		# 	# sys.stdout.flush()
		# 	for direction in result:
		# 		sequence = controls[direction]
		# 		for output in sequence.split():
		# 			self.window.postMessage(int(output, 0))
		# 			print direction, int(output, 0)
		# 			sys.stdout.flush()


		self.master.after(1, self.tree_preview)

if __name__ == '__main__':
	s = len(sys.argv)
	if s < 2:
		print 'Please enter window name.'
	else:
		name = sys.argv[1]
		park = Park(name, 'mario')