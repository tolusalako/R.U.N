#Toluwanimi Salako  (www.salakotech.com) 
import win32gui, win32ui, win32con, win32api
import cv2
from PIL import Image
from scipy import where, asarray
from gameobject import Object
import time

def find_objects_as_objects(img, objects, threshold = .6, all_ = True): #Multiple objects fix		
	img_rgb = asarray(img)
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

	found_objects = set()

	for obj in objects:
		img_copy = img_rgb.copy()
		template = cv2.imread(obj, 0)
		if template is None:
			continue
		w, h = template.shape[::-1]

		res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		loc = where( res >= threshold)
		for pt in zip(*loc[::-1]):
			name = obj.split('/')[-1].split('_')[0]
			found_objects.add(Object(name, pt, (w,h)))
		if ((not all_) and (len(found_objects) > 1)):
			break
	return found_objects

def find_objects_as_image(img, objects, threshold = .6, all_ = True, write_labels = False, labels = None):
	img_rgb = asarray(img)
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
	img_copy = img_rgb.copy()
	count = 0
	for obj in objects:
		template = cv2.imread(obj, 0)
		if template is None:
			continue
		w, h = template.shape[::-1]

		res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		loc = where( res >= threshold)
		name = obj.split('/')[-1].split('_')[0]
		for pt in zip(*loc[::-1]): #pt is the topleft corner
		 	cv2.rectangle(img_copy, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
		 	count += 1
		 	if ((write_labels) and (labels is not None) and (name in labels)):
				cv2.putText(img_copy, name, (pt[0]-5, pt[1]-3), cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, 200)
	 	
	 	if ((not all_) and (count > 0)):
	 		break
	return Image.fromarray(img_copy)

class GameWindow():
	def __init__(self, window_name, template_path):
		self.window_name = window_name
		self.templates = template_path
		self.source_list = ([], [])  #list of all matching windows
		win32gui.EnumWindows(self.__callback, self.source_list)  #populate list
		self.source_count = len(self.source_list)
		self.source = None
		self.shell = None

	def capture(self):
		if self.source is None:
			return None

		hwnd = self.source
 		windowSize = win32gui.GetWindowRect(hwnd)
 		hwin = win32gui.GetDesktopWindow()
 		width = windowSize[2] - windowSize[0]
		height = windowSize[3] - windowSize[1]
		hwindc = win32gui.GetWindowDC(hwin)
		srcdc = win32ui.CreateDCFromHandle(hwindc)
		memdc = srcdc.CreateCompatibleDC()
		bmp = win32ui.CreateBitmap()
		bmp.CreateCompatibleBitmap(srcdc, width, height)
		memdc.SelectObject(bmp)
		memdc.BitBlt((0, 0), (width, height), srcdc, (windowSize[0], windowSize[1]), win32con.SRCCOPY)
		bmpinfo = bmp.GetInfo()
		bmpstr = bmp.GetBitmapBits(True)
		img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
		win32gui.DeleteObject(bmp.GetHandle())
		memdc.DeleteDC()
		srcdc.DeleteDC()
		win32gui.ReleaseDC(hwnd, hwindc) 
		return img

	def pressKey(self, message, hold = -1):
		win32gui.ShowWindow(self.source, win32con.SW_SHOWNORMAL)
		win32api.SendMessage(self.source, win32con.WM_KEYDOWN, message, 1)
		if hold >= 0:
			time.sleep(hold)
			win32api.SendMessage(self.source, win32con.WM_KEYUP, message,1)

	def releaseKey(self, message):
		win32api.SendMessage(self.source, win32con.WM_KEYUP, message, 1)

	def size(self):
		if self.source is None:
			return None

		windowSize = win32gui.GetWindowRect(self.source)
 		width = windowSize[2] - windowSize[0]
		height = windowSize[3] - windowSize[1] 
		return (width, height)

	def set_source(self, source):
		self.source = source

	def release(self):
		pass

	def __callback(self, hwnd, lists):
		if win32gui.IsWindowVisible(hwnd):
			window_title = win32gui.GetWindowText(hwnd)
			if window_title != '':
				lists[0].append(hwnd)
				lists[1].append(str(len(lists[1])) + '-' + window_title)
		return True