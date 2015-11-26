from trakobject import Object
import gamewindow
from os import listdir

class Park():

	def __init__(self):
		pass






if __name__ == '__main__':
	template_path = "template/";
	objects = [f for f in listdir(template_path)]
	title = "mafia"
	source = 0;
	threshold = .3;

	gm = gamewindow.GameWindow(template_path)
	for i in range(len(gm.source_list[0])):
		if title in gm.source_list[1][i].lower():
			source = gm.source_list[0][i]
			break;

	if source != 0:
		temp_img = gm.capture(source)
		if temp_img != None:
			found_objects = gamewindow.find_objects_as_image(temp_img, [template_path + o for o in objects], threshold, all_ = False) 
			print [template_path + o for o in objects]
			found_objects.show()
