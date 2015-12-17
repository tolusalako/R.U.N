from trakobject import Object
import gamewindow
from os import listdir
import Tkinter as TK
from PIL import ImageTk, ImageFilter
from datetime import datetime
import sys, Queue
from collections import defaultdict

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
		result = set()
		if not self.top is None:
			result.add(self.top)
			self.direction[self.top] = 'top'
		if not self.left is None:
			result.add(self.left)
			self.direction[self.left] = 'left'
		if not self.right is None:
			result.add(self.right)
			self.direction[self.right] = 'right'
		if not self.topleft is None:
			result.add(self.topleft)
			self.direction[self.topleft] = 'topleft'
		if not self.topright is None:
			result.add(self.topright)
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

	return came_from, cost_so_far, found_goal





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

		self.window = gamewindow.GameWindow(self.template_path)
		for i in range(len(self.window.source_list[0])):
			if title in self.window.source_list[1][i].lower():
				source = self.window.source_list[0][i]
				break;
		self.window.set_source(source)
		self.width, self.height = self.window.size()
		self.setup()

		# t = self.get_tile((40, 40))
		# self.current_tree[t] = 0
		# L = self.generate_tree(t, 'right', 100)

		# while not t is None:
		# 	print t, t.cost, t.score
		# 	t = t.right
		# print
		# print self.tiles[-1][-1]


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
		if not result is None:
			score = cost * abs((result[0]- self.max_x) + (result[1] - self.max_y)) #http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html#S7
			if self.current_tree[result] != 0:
				for t in self.current_tree.keys():
					if t == result:
						#t.score, t.cost = score, cost
						t.score = score
						exec('root.'+direction+'= t')
						if steps > 0:
							self.generate_tree(t, direction, steps, score, cost + 1, set_last_step_to_goal)
						else:
							t.is_goal = True if set_last_step_to_goal else False
						return
			else:
				#result.score, result.cost = score, cost
				result.score = score
				exec('root.'+direction+'= result')
				self.current_tree[result] = score
				if steps > 0:
					self.generate_tree(result, direction, steps, score, cost + 1, set_last_step_to_goal)
				else:
					result.is_goal = True if set_last_step_to_goal else False
		else:
			root.is_goal = True if set_last_step_to_goal else False


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
		self.current_tree.clear() #clear?
		self.canvas.delete(TK.ALL)
		status = self.status.items()
		root = None
		for k,v in status:
			if v == 'mario':
				root = k
				self.current_tree[k] = -1
				self.generate_tree(k, 'left', 1, cost = 1)
				self.generate_tree(k, 'topleft', 1, cost = 1)
				self.generate_tree(k, 'right', self.max_x, cost = 1, set_last_step_to_goal = True)
				self.generate_tree(k, 'topright', 2, cost = 1)
				self.generate_tree(k, 'top', 1, cost = 1)


		result = a_star_search(self.char_location)
		# print result[0]
		# print
		# print result[1]
		# sys.stdout.flush()
		#print result[1]
		previous = result[2]
		while(previous is not None):
			w,h = self.tile_size
			start = previous
			end = start[0] + w, start[1]+h

			if previous.is_goal:
				self.canvas.create_rectangle(start, end, fill = 'green')
			else:
				self.canvas.create_rectangle(start, end, fill = 'black')
			previous = result[0][previous]

		# w,h = self.tile_size
		#for k,v in self.current_tree.items():
		# 	start = k
			
		# 	end = start[0] + w, start[1]+h
		# 	self.canvas.create_text(start, text = str(k.cost)) #Debug view cost and score
		# 	if k.is_goal:
		# 		self.canvas.create_rectangle(start, end, fill = 'green')
		# 	else:
		# 		self.canvas.create_rectangle(start, end, fill = 'black')


		self.master.after(1, self.tree_preview)

if __name__ == '__main__':
	s = len(sys.argv)
	if s < 2:
		print 'Please enter window name.'
	else:
		name = sys.argv[1]
		park = Park(name, 'mario')