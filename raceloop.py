import winAPI		#import my library created for the windows calls
import logic        #import the logic routines


logic.FindGame();

boost_gear = int(input("What gear should I boost on?: "));

while True: # TEMPORARY GIANT LOOP

	
	#logic.WaitForSceneChange();
	
	print "Beginning the pre-race logic...";
	
	#get our dc
	dc = winAPI.getDC();
	
	#Pre-race logic
	logic.WaitForStaging(dc);

	#Race found, prep for launch

	logic.DetectRaceType(); #new thread, gets its own dc
	logic.Staging(dc);

	print "Past staging"

	#winAPI.Wait(1); # sleep for one second to make sure we don't have any stalls


	#shifting logic
	logic.DetectSceneChangeStart(); #start our scene detection thread.
	logic.Race(boost_gear,dc);
	logic.DetectSceneChangeStop(); #Stop our scene detection thread.

	#release our DC
	winAPI.releaseDC(dc);
	
	print "The race has ended. Quitting, for now..."
	