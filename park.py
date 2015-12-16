from trakobject import Object
import gamewindow
from os import listdir
import Tkinter as TK
from PIL import ImageTk, ImageFilter
from datetime import datetime
import sys
from collections import defaultdict

class Tile():
	def __init__(self, location, above = None, below = None, left = None, right = None):
		self.location = location
		self.above = above
		self.below = below
		self.left = left
		self.right = right
		self.score = 0

def get_tile(screen_size, obj_loc, obj_size):
	width, height = screen_size
	w,h = obj_size
	for row in height:
		for col in width:
			

class Park():
	def __init__(self, name, main_character):
		self.template_path = "template/";
		self.objects = [f for f in listdir(self.template_path)]
		title = name
		source = 0;
		self.threshold = .7
		self.status = defaultdict(list)
		self.destroy = False
		self.char = main_character
		self.tile_size == (33, 33)

		self.window = gamewindow.GameWindow(self.template_path)
		for i in range(len(self.window.source_list[0])):
			if title in self.window.source_list[1][i].lower():
				source = self.window.source_list[0][i]
				break;
		self.window.set_source(source)
		self.width, self.height = self.window.size()
		self.setup()

	def setup(self):
		self.downsize = 1
		self.generate_tiles()

		self.master = TK.Tk()
		self.base = TK.Frame(self.master)
		#self.master.protocol('WM_DELETE_WINDOW', self.__on_exit_preview)
		self.master.wm_title("Preview")
		#self.master.iconbitmap('icon.ico')
		self.canvas = TK.Canvas(master = self.base, background = "#FFFFFF", height = self.height*self.downsize,
		 width = self.width*self.downsize)
		self.canvas.grid(row = 0, column = 0, sticky = TK.W)

		self.save_btn = TK.Button(master = self.base, text = 'Save', command = self.save_temp)
		self.save_btn.grid(row = 1, columnspan = 20, sticky = TK.W + TK.E)

		self.base.pack()
		self.preview_loop()
		#self.hud_preview()
		#self.update_status()
		self.master.mainloop()

	def update_status(self):
		self.temp_img = self.window.capture()
		if self.temp_img != None:
			self.found_objects = gamewindow.find_objects_as_objects(self.temp_img, 
				[self.template_path + o for o in self.objects], self.threshold)
			self.status = defaultdict(list) #TODO: Instead of creating new, clear individual keys
			for o in self.found_objects:
					self.status[o.name].append(get_tile(o.location))
			self.master.after(1, self.update_status)

	def generate_tiles(self):
		self.tiles = []
		width, height = self.window.size()
		w, h = self.tile_size
		for row in range(0, height, h):
			R = []
			for col in range(0, width, w):
				R.append(Tile((col, row)))
			self.tiles.append(R)

	def get_tile(x, y):
		w, h = self.tile_size
		return self.tile[y/h][x/w]

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

				w,h = o.size
				start = o.location
				end = start[0] + w, start[1]+h
				self.canvas.create_rectangle(start, end, fill = color)
			self.master.after(1, self.hud_preview)

if __name__ == '__main__':
	s = len(sys.argv)
	if s < 2:
		print 'Please enter window name.'
	else:
		name = sys.argv[1]
		park = Park(name)