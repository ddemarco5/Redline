import winAPI		#import my library created for the windows calls
import logic        #import the logic routines


logic.FindGame();

while True:

	#FOR FINDING PIXEL VALUES AND COLORS
	cursor_pos = (winAPI.getRelativeCoords(winAPI.getCursor()),);
	
	#color = winAPI.getPixelColor(cursor_pos)
	color = logic.GetCoordsColor(cursor_pos)
	print "Pos:",cursor_pos,"Color:",color;
	
	winAPI.Wait(.25);
	