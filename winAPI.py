from ctypes import *
from ctypes.wintypes import RECT
import time

#dc = windll.user32.GetDC(0)
nitro_window_coords = [-1,-1];
nitro_window_found = False;

#CONSTANTS
NitroTitle = "Nitro Nation"


# struct for point color functions
class POINT(Structure):
    _fields_ = [("x", c_ulong), ("y", c_ulong)]

SendInput = windll.user32.SendInput

# C struct redefinitions 
PUL = POINTER(c_ulong)
class KeyBdInput(Structure):
    _fields_ = [("wVk", c_ushort),
                ("wScan", c_ushort),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(Structure):
    _fields_ = [("uMsg", c_ulong),
                ("wParamL", c_short),
                ("wParamH", c_ushort)]

class MouseInput(Structure):
    _fields_ = [("dx", c_long),
                ("dy", c_long),
                ("mouseData", c_ulong),
                ("dwFlags", c_ulong),
                ("time",c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(Structure):
    _fields_ = [("type", c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def Wait(time_to_sleep):
	time.sleep(time_to_sleep);

def Time():
	return time.time();
	
def GetGameCoords():
	return nitro_window_coords;

def GameFound():
	return nitro_window_found;

def PressKey(hexKeyCode):

    extra = c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( hexKeyCode, 0x48, 0, 0, pointer(extra) )
    x = Input( c_ulong(1), ii_ )
    windll.user32.SendInput(1, pointer(x), sizeof(x))

def ReleaseKey(hexKeyCode):

    extra = c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( hexKeyCode, 0x48, 0x0002, 0, pointer(extra) )
    x = Input( c_ulong(1), ii_ )
    windll.user32.SendInput(1, pointer(x), sizeof(x))
	
def KeyPress(keycode, delay):
	PressKey(keycode)
	time.sleep(delay)
	ReleaseKey(keycode)

#End all that keypress jazz
	
def findNitroCoords():
	EnumWindows = windll.user32.EnumWindows
	EnumWindowsProc = WINFUNCTYPE(c_bool, POINTER(c_int), POINTER(c_int))
	GetWindowText = windll.user32.GetWindowTextW
	GetWindowTextLength = windll.user32.GetWindowTextLengthW
	GetWindowRect = windll.user32.GetWindowRect
	IsWindowVisible = windll.user32.IsWindowVisible
 
	nitro_hwnd = 0; 	#the window that nitro will be if it is found.
 
	#titles = []
	#The "callback" if you will, for the EnumWindows function
	def foreach_window(hwnd, lParam):
	#	if IsWindowVisible(hwnd):
		global nitro_window_found;
		global nitro_window_coords;
		length = GetWindowTextLength(hwnd)
		buff = create_unicode_buffer(length + 1)
		GetWindowText(hwnd, buff, length + 1)
		string_title = buff.value.decode("utf-8");
		if string_title == NitroTitle:
			nitro_hwnd = hwnd;
			nitro_window_found = True;
			nitro_rect = RECT();
			GetWindowRect(hwnd,byref(nitro_rect));
			nitro_window_coords[0] = nitro_rect.left;
	  		nitro_window_coords[1] = nitro_rect.top;
			
		#titles.append(buff.value)
		#return True
	EnumWindows(EnumWindowsProc(foreach_window), 0)
		
 
	
def getRelativeCoords(tuple):
	return((tuple[0]-nitro_window_coords[0]),(tuple[1]-nitro_window_coords[1]))
	
def getCursor():
	pt = POINT()
	windll.user32.GetCursorPos(byref(pt));
	return (int(pt.x), int(pt.y));

#required when a trying to get the pixel value from another thread.
def getDC():
	dc = windll.user32.GetDC(0);
	if dc is None:
		print "Error getting DC";
		exit(1);
	print "Got DC"
	return dc;

def releaseDC(dc):
	ret = windll.user32.ReleaseDC(0,dc);
	if ret != 1:
		print "The DC was not released."
		exit(1);
	print "Released DC"
		
#Takes relative coordinates
def getPixelColor(tuple,dc):
	#getDC();   #we need to do this in order to get correct pixel data from multiple threads for whatever reason.
	#make absolute
	abs_coords = ((tuple[0] + nitro_window_coords[0]), (tuple[1] + nitro_window_coords[1]));
	winreturn = windll.gdi32.GetPixel(dc,abs_coords[0],abs_coords[1]);
	#print winreturn;
	#It reads in as BGR, so we correct them in the return
	Red =  winreturn & 255
	Green = (winreturn >> 8) & 255
	Blue =   (winreturn >> 16) & 255;
	#releaseDC();
	return (Red,Green,Blue);

user = windll.LoadLibrary("c:\\windows\\system32\\user32.dll")
h = user.GetDC(0)
gdi = windll.LoadLibrary("c:\\windows\\system32\\gdi32.dll")

#print hex(getpixel(500,500));

# Now begins the actual code, first off, get the top left position of the game window.

#raw_input('Press enter to get position'); #makes us press enter

#mainwindow_topleft = getCursor();
#print mainwindow_topleft;

#raw_input('Now press enter to get the offset coords');
#offsetcoords = getrelativecoords(getCursor());
#print offsetcoords;