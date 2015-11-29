from trakobject import Object
import gamewindow
from os import listdir
import Tkinter as TK
from PIL import ImageTk, ImageFilter
from datetime import datetime

class Park():
	def __init__(self, name):
		self.template_path = "template/";
		self.objects = [f for f in listdir(self.template_path)]
		title = name
		source = 0;
		self.threshold = .7

		self.window = gamewindow.GameWindow(self.template_path)
		for i in range(len(self.window.source_list[0])):
			if title in self.window.source_list[1][i].lower():
				source = self.window.source_list[0][i]
				break;
		self.window.set_source(source)
		self.width, self.height = self.window.size()

	
	def run(self):
		self.temp_img = self.window.capture()

		self.temp_img = self.temp_img.filter(ImageFilter.FIND_EDGES)
		self.temp_img.save('emboss.png')
		if self.temp_img != None:
			found_objects = gamewindow.find_objects_as_image(self.temp_img, [self.template_path + o for o in self.objects], self.threshold, all_ = True) 
			# print [template_path + o for o in objects]
			found_objects.show()

	def save_temp(self):
		self.temp_img.save(str(datetime.now().strftime("%I-%M %p")) + '.png')

	def preview(self):
		self.downsize = .5
		self.destroy = False
		self.master = TK.Tk()
		self.base = TK.Frame(self.master)
		#self.master.protocol('WM_DELETE_WINDOW', self.__on_exit_preview)
		self.master.wm_title("Preview")
		#self.master.iconbitmap('icon.ico')
		self.canvas = TK.Canvas(master = self.base, background = "#FFFFFF", height = self.height*self.downsize, width = self.width*self.downsize)
		self.canvas.grid(row = 0, column = 0, sticky = TK.W)

		self.save_btn = TK.Button(master = self.base, text = 'Save', command = self.save_temp)
		self.save_btn.grid(row = 1, columnspan = 20, sticky = TK.W + TK.E)

		self.base.pack()
		self.preview_loop()
		self.master.mainloop()

	def __on_exit_preview(self):
		self.destroy = True

	def preview_loop(self):
		self.temp_img = self.window.capture()
		if self.temp_img != None:
			self.found_objects = gamewindow.find_objects_as_image(self.temp_img, [self.template_path + o for o in self.objects], self.threshold, all_ = True)
			self.photo_preview = self.found_objects.copy()
			self.photo_preview = ImageTk.PhotoImage(self.found_objects.resize((int(self.width*self.downsize), int(self.height*self.downsize))))
			self.canvas.create_image((0, 0), image = self.photo_preview, anchor = TK.N +TK.W)
			self.master.after(1, self.preview_loop)



if __name__ == '__main__':
	park = Park('mafia')
	park.preview()