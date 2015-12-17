from trakobject import Object
import gamewindow
from os import listdir
import Tkinter as TK
from PIL import ImageTk, ImageFilter
from datetime import datetime
import sys
from collections import defaultdict

class Tile(tuple):
	def __init__(self, location, top = None, left = None, right = None, topright = None, topleft = None):
		tuple.__init__(location)
		self.top = top
		self.left = left
		self.right = right
		self.topleft = topleft
		self.topright = topright
		self.score = 0
			

class Park():
	def __init__(self, name, main_character):
		self.template_path = "template/";
		self.objects = [f for f in listdir(self.template_path)]
		title = name
		source = 0;
		self.threshold = .7
		self.status = defaultdict(str) #key = location, value = object_name
		self.destroy = False
		self.char = main_character
		self.tile_size = (33, 33)
		self.current_tree = defaultdict(int) #key = location, value = score

		self.window = gamewindow.GameWindow(self.template_path)
		for i in range(len(self.window.source_list[0])):
			if title in self.window.source_list[1][i].lower():
				source = self.window.source_list[0][i]
				break;
		self.window.set_source(source)
		self.width, self.height = self.window.size()
		self.setup()

		# t = self.get_tile((40, 40))
		# self.current_tree[t] = 1
		# L = self.generate_tree(t, 'right', 100)

		# while t != None:
		# 	print t, t.score
		# 	t = t.right


	def setup(self):
		self.downsize = 1
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
		if self.temp_img != None:
			self.found_objects = gamewindow.find_objects_as_objects(self.temp_img, 
				[self.template_path + o for o in self.objects], self.threshold)
			self.status = defaultdict(str)
			for o in self.found_objects:
				t = self.get_tile(o.location)
				if t is not None:
					self.status[t] = o.name
			self.master.after(1, self.update_status)

	def generate_tree(self, root, direction, steps = 1, score = 1):
		steps -= 1
		result = {
			'right' : self.get_tile_in_direction(root,'right'),
			'left' : self.get_tile_in_direction(root,'left'),
			'top' : self.get_tile_in_direction(root,'top'),
			'down' : self.get_tile_in_direction(root,'down'),
			'topleft' : self.get_tile_in_direction(root,'topleft'),
			'topright' : self.get_tile_in_direction(root,'topright')
		}.get(direction, 'right')
		if not result is None:
			if self.current_tree[result] != 0:
				exec('root.'+direction+'= t')
				if steps > 0:
					self.generate_tree(t, direction, steps)
				return

			exec('root.'+direction+'= result')
			self.current_tree[result] = score
			if steps > 0:
				self.generate_tree(result, direction, steps)

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
		if self.temp_img != None:
			labels = ('mario', 'goomba', 'pickup')
			self.found_objects = gamewindow.find_objects_as_image(self.temp_img, [self.template_path + o for o in self.objects], self.threshold, write_labels = True, labels = labels)
			self.photo_preview = self.found_objects.copy()
			self.photo_preview = ImageTk.PhotoImage(self.found_objects.resize((int(self.width*self.downsize), int(self.height*self.downsize))))
			self.canvas.create_image((0, 0), image = self.photo_preview, anchor = TK.N +TK.W)
			self.master.after(1, self.preview_loop)


	def hud_preview(self):
		self.temp_img = self.window.capture()
		if self.temp_img != None:
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
		print len(status)
		for k,v in status:
			if v == 'mario':
				self.current_tree[k] = -1
				self.generate_tree(Tile(k), 'left', 1)
				self.generate_tree(Tile(k), 'topleft', 1)
				self.generate_tree(Tile(k), 'right', 1)
				self.generate_tree(Tile(k), 'topright', 1)
				self.generate_tree(Tile(k), 'top', 1)
			elif v == 'goomba':
				self.current_tree[k] = 1
				self.generate_tree(Tile(k), 'left', 1, -5)
		w,h = self.tile_size

		for k,v in self.current_tree.items():
			start = k
			
			end = start[0] + w, start[1]+h
			self.canvas.create_rectangle(start, end, fill = 'black')
		self.master.after(2, self.tree_preview)


		#key = location, value = '' if not generated else 'x' #x 

if __name__ == '__main__':
	s = len(sys.argv)
	if s < 2:
		print 'Please enter window name.'
	else:
		name = sys.argv[1]
		park = Park(name, 'mario')