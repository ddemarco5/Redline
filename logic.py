import winAPI		#import my library created for the windows calls
import thread

#color declares
WHITE = (255,255,255);
BLACK = (0,0,0);

LaunchLightCoords = (641,458);
ShiftLightCoords = (670,700);  #(671,702)           #673, 703 this is the og

#ShiftLightCoords = (670,701);
SceneChangeCoords = ((1083,67), #will be black on scene change
					(1120,568),		#these two are the shifter
					(1122,640),
					(567,553))

PreRaceCoords = ((1105, 378),	#these two are the rev pedal
				(1134,366),
				#(194,616),		#these two are the nos bottle
				#(168,578),
				(1120,568),		#these two are the shifter
				(1122,640));

#Launch declares
UndergroundLightCoords = (644, 456);
UndergroundLightDark = (107, 162, 74);
UndergroundLightBright = (97, 226, 119);

RegularLightCoords = (715, 452);
RegularLightDark = (109, 150, 77);
RegularLightBright = (232, 251, 243);

ShiftKey = 0x26;	#Up Arrow
LaunchKey = 0x28;	#Down Arrow
BoostKey = 0xA0;	#Left Shift
EnterKey = 0x0D;	#Enter Key
SpaceBar = 0x20;    #Spacebar


#"daemon" thread flags
#this one is for scenechange
RunDetectSceneChange = False;
SceneChangeDetected = False;

#must take an ARRAY OF ARRAYS
def GetCoordsColor(coord_array,dc):
	color_array = [];
	for coord in coord_array:
		color_array.append(winAPI.getPixelColor(coord,dc))
	return color_array;

#take an array of coords, get their colords, and compare those to an expected color
def CheckCoordsColor(coords_array,color_to_check, dc):
	colors = GetCoordsColor(coords_array,dc);
	for color in colors:
		if color != color_to_check:
			return False;
	return True;

#our scene change detection declares.
#wrapper function for returning the scene change detected bool.
def IsSceneChange():
	global SceneChangeDetected;
	return SceneChangeDetected;

#detectscenechange is the logic
def DetectSceneChange():
	global SceneChangeDetected;
	print "Starting scene change detection.";
	dc = winAPI.getDC();
	while RunDetectSceneChange:
		if CheckCoordsColor(SceneChangeCoords,BLACK,dc):
			SceneChangeDetected = True;
		else:
			SceneChangeDetected = False;
	winAPI.releaseDC(dc);
	print "Stopped scene change detection."

#start the scenechange detection in a new thread.	
def DetectSceneChangeStart():
	global RunDetectSceneChange, SceneChangeDetected;
	RunDetectSceneChange = True;
	SceneChangeDetected = False;
	try:
		thread.start_new_thread(DetectSceneChange,());
	except:
		print "Error: unable to start scene change detection thread."

#stop the scene change detection thread		
def DetectSceneChangeStop():
	global RunDetectSceneChange;
	RunDetectSceneChange = False;
	

def LaunchRegularRace(dc):
	launch_light_pixel = winAPI.getPixelColor(RegularLightCoords,dc);
	while launch_light_pixel != RegularLightBright:
		launch_light_pixel = winAPI.getPixelColor(RegularLightCoords,dc);
	print "LAUNCH!";
	winAPI.KeyPress(LaunchKey, .15);

def LaunchUndergroundRace(dc):
	launch_light_pixel = winAPI.getPixelColor(UndergroundLightCoords,dc);
	while launch_light_pixel != UndergroundLightBright:
		launch_light_pixel = winAPI.getPixelColor(UndergroundLightCoords,dc);
	print "LAUNCH!";
	winAPI.KeyPress(LaunchKey, .15);

#Returns 0 for no race type detected, 1 for underground race, 2 for standard timed light
def DetectRaceTypeFunction():
	print "\nStarted Detection Routine"
	timeout = winAPI.Time() + 5; #5 seconds from now.
	dc = winAPI.getDC();
	while (winAPI.Time() <= timeout):     #only run this loop for five seconds, to correctly detect when there isn't a special race type
		if winAPI.getPixelColor(UndergroundLightCoords,dc) == UndergroundLightDark:
			print "Underground Launch Detected"
			LaunchUndergroundRace(dc);
			break;
		if winAPI.getPixelColor(RegularLightCoords,dc) == RegularLightDark:
			print "Regular Launch Detected"
			LaunchRegularRace(dc);
			break;
	winAPI.releaseDC(dc);
	#print "No special race type detected."
	
#Calls a threaded function because we need to detect a race type while the bot is staging.
#In this case we don't need handling, because the thread will simply execute keypresses.
def DetectRaceType():
	try:
		thread.start_new_thread(DetectRaceTypeFunction,())
	except:
		print "Error: unable to start race detection thread."

	
def FindGame():
	winAPI.findNitroCoords();
	nitro_window_coords = winAPI.GetGameCoords();
	if winAPI.GameFound() == False:
		print "Nitro Nation was not found. Try executing when the game is running."
		exit(1);
	elif nitro_window_coords[0] < 0:
		print "Nitro Nation found, but is minimized or something weird. Bring it into view and restart program.";
		print nitro_window_coords;
		exit(1);
	else:
		print "Nitro Nation was found, these are its window coords. Don't move the game window!"
		print "X:", nitro_window_coords[0], " Y:", nitro_window_coords[1];

def WaitForStaging(dc):
	print "Waiting for staging."
	
	#loop until the expected pixels are white.
	while not CheckCoordsColor(PreRaceCoords,WHITE,dc):
		winAPI.Wait(1.00);
	
		
def Staging(dc):
	print "Pre-race. Staging.";
	winAPI.Wait(1.0);	#Wait for a bit to make sure the game is ready to recieve inputs after loading.
	initial_throttle = True;
	#pedal_color = winAPI.getPixelColor(PreRaceCoords[0]);
	#while (pedal_color == (255,255,255)): #pedal is still while. Race has not yet started.
	while (CheckCoordsColor(PreRaceCoords,WHITE,dc)): #pedal is still while. Race has not yet started.
		#pedal_color = winAPI.getPixelColor(PreRaceCoords[0]);
		shift_color = winAPI.getPixelColor(ShiftLightCoords,dc);
		if initial_throttle:
			winAPI.KeyPress(SpaceBar,.8); #.5 adjust this to have it fall well when the race starts. This will change per car and is far from a perfect solution.
			initial_throttle = False;
		#if ((shift_color[0] >= 200) and (shift_color[1] >= 200)) and not initial_throttle: #if yellow and not initial throttle
		if not initial_throttle: #if yellow and not initial throttle
			winAPI.KeyPress(ShiftKey,.16); #.5
			winAPI.Wait(.7); #.8
	#winAPI.Wait(.5);  #wait a half a second before shifting so we don't stall the car

#shifting check needs to be fast.	
def Race(gear_to_boost,dc):
	print "Racing";
	#shifting logic
	shifted = False;
	gear = 1;
	shift_color = winAPI.getPixelColor(ShiftLightCoords,dc);   #get the shift colors initially
	#time = winAPI.Time();
	while not IsSceneChange(): #while not black, meaning the race is over. 
		shift_color = winAPI.getPixelColor(ShiftLightCoords,dc);
		#ensure that the light is either green or red, but not yellow by xoring the r and g values of the rgb color
		#if ((shift_color[0] >= 250) != (shift_color[1] >= 200)) and not shifted:
		if (((shift_color[0] >= 250) and (shift_color[1] <= 200)) or ((shift_color[0] <= 200) and (shift_color[1] >= 250))) and not shifted:
			print "SHIFT!", gear, shift_color;
			winAPI.KeyPress(ShiftKey,0);
			shifted = True;
			if gear <= gear_to_boost:
				print "Boost!";
				winAPI.KeyPress(BoostKey,.5);
			gear = gear + 1;
		#The shift color is neither yellow nor green, so we can toggle the shifted flag to off. This prevents fluttering of the shift key.
		if ((shift_color[0] < 250) and (shift_color[1] < 250)) and shifted:
			shifted = False;
		#newtime = winAPI.Time();
		#print "Looptime:",newtime-time;
		#time = newtime;