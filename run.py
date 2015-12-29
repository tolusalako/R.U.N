from gameobject import Object
import gamewindow
from os import listdir
import Tkinter as TK
from PIL import ImageTk
from datetime import datetime
import sys, Queue
from collections import defaultdict
import time

controls = {
	'top' : 0x58,
	'right': 0x27,
	'left': 0x25
}



class Tile(tuple):
	def __init__(self, location, top = None, left = None, right = None, topright = None, topleft = None,
		score = 0, cost = 0):
		tuple.__init__(location)
		self.x = self.__getitem__(0)
		self.y = self.__getitem__(1)


class RunAI():
	def __init__(self, name, main_character):
		self.template_path = "template/";
		self.objects = [f for f in listdir(self.template_path)]
		title = name
		source = 0;
		self.threshold = .75
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
		self.generate_tiles() #Only call once

		self.master = TK.Tk()
		self.base = TK.Frame(self.master)
		self.master.wm_title("RunAI")
		self.canvas = TK.Canvas(master = self.base, background = "#FFFFFF", height = self.height*self.downsize,
		 width = self.width*self.downsize)
		self.canvas.grid(row = 0, column = 0, sticky = TK.W)

		self.save_btn = TK.Button(master = self.base, text = 'Save', command = self.save_temp)
		self.save_btn.grid(row = 1, columnspan = 20, sticky = TK.W + TK.E)

		self.base.pack()
		self.update_status()
		# self.preview_loop() #If you want preview, comment update_status(), run(), and master.withdraw()
		self.run()
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
					heighest = 4
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
		self.preview_img.save(str(datetime.now().strftime("%I-%M %p")) + '.png')

	def __on_exit_preview(self):
		self.destroy = True

	def preview_loop(self):
		self.preview_img = self.window.capture()
		if not self.preview_img is None:
			labels = ('mario', 'goomba', 'pickup', 'block')
			self.found_objects = gamewindow.find_objects_as_image(self.preview_img, 
				[self.template_path + o for o in self.objects], self.threshold, write_labels = True, labels = labels)
			self.photo_preview = ImageTk.PhotoImage(self.found_objects.resize((int(self.width*self.downsize), int(self.height*self.downsize))))
			self.canvas.create_image((0, 0), image = self.photo_preview, anchor = TK.N +TK.W)
			self.master.after(1, self.preview_loop)

	def run(self):
		self.current_tree.clear() #clear
		status = self.status.items()
		root = None
		for k,v in status:
			if v == 'mario':
				root = k
				break


		KEY_PRESS = 0.3
		KEY_PRESS_SMALL = 0.15
		if root is not None:
			obstacle, pit = self.check_forward_for_obstacles(root, steps = 5)
			print obstacle, pit
			sys.stdout.flush()
			self.window.pressKey(controls['right'])
			if pit == obstacle == 0:
				pass # self.window.pressKey(controls['right'])
			else:
				self.window.pressKey(controls['top'])
				time.sleep(KEY_PRESS_SMALL * max(obstacle, pit))
				self.window.releaseKey(controls['top'])
				self.window.releaseKey(controls['right'])
		self.master.after(0, self.run)

if __name__ == '__main__':
	s = len(sys.argv)
	if s < 2:
		print 'Please enter window name.'
	else:
		name = sys.argv[1]
		r = RunAI(name, 'mario')