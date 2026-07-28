

27.7.26


1) follow mode: seems like the zooming does not work properly, panning is now ok but mostly it is too zoomed in to match everything visible on tabula, works especially bad in seg II and >X


1) debounce follow button, do not click on map there..
2) if user location map tiles are loading show loading animation, now there is noting, takes like few seconds to load on startup
3) not the follow algorithm is really weird. zoooms in very close if i view segment II, or VII e.g. zoom is very close, showing just 2-3 places on user location map although there is full segment visible on tabula


now the follow is too zoomed out. find out which places are visible on tabula to determine which zoom/pan on user loc map is required. please present the detailed algorithm to me as flowchart and propose possible solutions/algorithms to solve that..



1) follow button shall have black text other wise its not visible. the follow mode does not work at all seems not to move properly, please analyze in detail and propose solutions for me to decide. Follow mode shall zoom/pan the user location map to the current visible places on the tabula. if user pans/zooms on tabula, user loc map shall follow!



1) follow button shall be on top right of the map not in the top bar and be transparent if not active, remove padding around the text as much as possible. 
2) the follow mode does not work properly, the user loc map shall show what is visible on the current tabula view
3) in country mode only on user loc map very zoomed in like inside a country the individual places shall be selectable


1) if i open user loc map in mobile seems the user loaction is panned to very right, the user location shall be in the center! 
1.1) add a small button in user loc map top right "follow" which follows the tabula windows view in the user loaction map zoom/pan 

2) add country mode place dot size slider in developer settings panel so i can adjust this. save is persistent!
3) if i select a country on map do not pan/zoom the user loaction map!
4) rename "tour" button to "demo"




optimization for index: 

0) please start the server
1) reduce size of user locaiton crosshair on tabula in zoomed out mode. zoomed in its ok
2) https://tp-online.ku.de/trefferanzeige.php?id=1456 missing please add
3) Changing to country mode removes the user selected icon on user location map, now it stays indefinietely
4) Zoom in the user location map more when canging to country mode, 4-5 countries shall be in user location map window around the current country.
5) Translate wiki texts to selected language (german and english possible, translate from other languages if required for some wiki entries)
6) If a new place is selected on tabula an info panel opens which shall always open scrolled up!
7) If i pan the user lcoation map seems it opens many hover infos which sometimes persist so looks very bad, maybe add a small debounce!
8) Somehow make it clear the tabula and the interpretation of science are not 100% correct in about and maybe in a hint on startup to explain the system of the map


Index on phone: 
1. Reduce size of"deactivate country mode" icon padding very strongly on top and bottom as well
2. If I resize or move the user location map the tabula zoom buttons do not adapt 
3. Resize/move info panel very buggy the resize label moves out of screen sometimes, the info panel bottom never shall be outside the window 


17.07.2026

https://tp-online.ku.de/trefferanzeige.php?id=2910 missing as well

1) import https://tp-online.ku.de/trefferanzeige.php?id=508 to database it is missing

14.7.26

Optimizations for Index general: 
	1. Krim on user loc map is still russian color, draw it in ukrainian color
	2. Crosshair text larger for mobile
	3. Reduce size of the crosshair on map by 20%
	4. User location does not work often, if I select on Mediterranean sea it often places the marker on africa ob tabula, mainly obvious for user in case of mediterranean sea. Please think in detail about options and let me decide
	5. Info panel resizet does not work often,  the vertical size cannot be changed, as it is defined by screen bottom and user selected top, the width by the user selection as well. The with alignment marker moves away and cannot be touched any more then I move the window
	6. User location map resize shall not be possible outside the window so user cannot select the resize button any more. The window is the limit!
	7. SEO optimization for Web
	8. Translate wiki texts to selected language
	9. When tour is started, close all open windows before start. Shorten the about window open time by 30% 
	
Index on Tablet and phone


Index on phone: 
	1. Reduce size of"deactivate country mode" icon padding very strongly 
	2. User location map: Remove hover Info on click, seems sometime the user loc map pans and then the hover info pops out but does not go away
	3. Seems after pushing GPS position button on user LOC map the tabula pans to another place,don't understand why
	4. Seems category menu does not open at first touch, very strange, maybe debouncing required. 
Seems info panel sometimes closes after resizing, maybe debouncing required as well?

5.7.26

the full demo shall be like before: about panel, user loc map, country mode, isolate, category menu select names please check

1) the current tour button animation shall happen at every startup. the actual tour shall be the one opening all panels, about, user loc map and category


do not open info panel on gps location on startup


1) place info on user location map has 15s timeout, reduce size by 30% 
2) put the "tour" button below the about button, make it small to its readable but small enough
3) do not show the about panel but keep the button flash to hint the user to the about info, flash user location map icon and category icon as well
4) crimea is still in russian color on user locaiton map.


1) lets decide about demo behavior, how to handle. have a button somewhere to start again and show once only per user (device/IP?
2) for phones add info that there is a website and shall visit this page for best experience on a large screen for improve User experience
3) on startup pan the tabula map to the user location
4) text for crosshair on tabula "you are here" (translate to selected language) and "Picked Location"
5) user location map: crimea shall be part of Ukraine, now seems the country color is russia but all the places are ukraine
6) if i click outside a place on tabula the current place is not deselected, something went wrong with implementation? 20s timeout works
7) can you make the roads on user location map 20% more thicker?


1) selected place in user location map info is smaller font and more to the bottom
2) in phone portrait mode info panel cannot be resized, seems if i touch the resize icon, it moves to the bottom outside the window
3) if on tabula map if i click outside of a place, remove the current place selection. the place selection has a timeout of 20s as well
4) add a small text label on bottom right of the crosshairs on tabula (red and blue) with info


1) user location map: country overlaps with selected place.
1.2) tablet/phone:  in country mode only with pretty much zoomed in a place can be selected
2) phone/tablet mode: info panel padding left right too large, shall be less than a font letter wide similar to the large screen version!
3) in country mode sometinmes the red crosshair vanishes but reappiers after deactivating country mode
4) seems if gps is not permitted there is not red crosshair on tabula with gps allowed it works
5) if GPS is not permitted ask again to enable when clicking GPS location
6) for tablet mode (9-14 inches) please have 10% larger fonts and icons, now they are pretty small



 0) copy red teardrop size/shape from the blue one
 1) without GPS use the default location for the red teardrop/crosshair location

0) red teardrop missing on user location map of user gps loction, blue teardrop is if user selects another place on the map, the red gps user location teardrop stays there all the time!
1) user loc map: shop the place info on clicked much on the bottom of the user loc map as it blocks selection of places etc
2) always show red crosshair un tabula map of user gps location, the user selected location adds second blue crosshair on tabula!
3) if click gps it shall select the place on tabula and pan to this place/location on tabula as well --> fix
4) push to gh for testing

Optimizations for Index: 
	1. Info panel resize changes width only, as height is defined by the content
	2. User GPS location icon missing on user location map. Shall be red location icon
	3. Show the user gps location cross hair on tabula map after hitting gps




Index on Tablet and phone
User location map: Reduce padding in country bar and buttons and the height of the bar, there is lot of empty space which reduces space for the map. But leave font and icon size the same!

if i resize the info panel or user loc map  it has weird position if i change orientation afterwards. needs to have a position in landscape and portrait mode which are each modifiable!

can you make the +- icon size in info panel map preview like 30% smaller?
no improvement, please roll back the change. there is padding now around the info panel, there shall be minimal padding see screenshot padding (space around panel content to border shall be rather small 

still if map preview is small on info panel its totally hidden with text from OSM like "report a problem" etc, please remove the ext so map is visible

there is strange behaviro of info panel resize icon, it has a fixed position in the info panel height so if i scroll down in info panel the icon moves up as well

rounded edges on all sides of user loc map window, info panel


for phone: can you hide the contributors etc text on the map preview in info panel?


1) the user location map window shall have rounded edges like the info panel!



1) phone/tablet: clicking legend icon still in user lcoation map still opens the place behind the legend icon. everything behind the legend icon is not selectable!
2) mobile/tablet: info panel resize does not work below certain value, please make sure the link icons and wiki picture, map preview resize when panel gets smaller.
3) phone/tablet: user loca map legend button shall be on the right side, otherwise it overlaps with category icon on bottom left.



1) seems on phone and tablet mode the info panel does not rearrange when lowering size, seems to be dependant on the map preview inside
2) phone/tablet: clicking on the legend does not open a place!
3) phone/tablet: reduce padding in country mode icon left and right of country mode text, there is much space
4) phone/tablet: reduce size of the +- buttons in user location map by 30%


1) reduce size of the fullscreen button to fit the height of +- buttons combined2) 
2) if i activate country mode seems like transparency is too low or all countries are selected so there is double 
3) decrease user location map places dot size in country mode zoomed out state
4) in phone and tablet mode reduce size of the user loc map resize icon, now leged is hardly selectable 


i cannot change the user location map size in tablet and phone mode

4.7.26

make it possible to change location and width of the info panel and user location map in phone or tablet 
		

Optimizations for Index: 
	1. If info panel is closed do not deselect the place on tabula

Index on Tablet and phone
	1. User location map: Reduce padding in country bar and buttons and the height of the bar, there is lot of empty space which reduces space for the map. But leave font and icon size the same!
	2. For non road stations do not zoom in too much, all of the selected place shall be visible on screen

    
		
Optimizations for Index: 
	1. Dont see the gps icon on the user location map

Index on Tablet and phone
	1. On user location map selection of a place, leave the user location map zoom unchanged but change the tabula map zoom to map to maxixmum in case of phone and a little more than currently implement for tablets

Optimizations for Index: 	
		
	1. Icon for users actual gps location on user location map shall be a different icon than the one the user selects on the map arbitrarily, like a red version of the current blue user location icon

Index on Tablet and phone
	1. 

Index for phone screens:
	1.  zoom in to max zoom on user location place selected
	2. Increase font size of search field by 20%
	3. User location map:
		a. Reduce padding size of the icons in the user loca map, but keep font and icon size inside the buttons
		b. Make the bar with the buttons less high but keep button size and font size


Index for tablet screen ~9-14 inch

	1. In portrait mode the info shall begin 1/4 of the with of screen and go all the way to the right
Increase font size of search field by 50%




Optimizations for Index: 
		
	1. Remove major city category this is double
	2. Remove round user map selected place selected indication ring around place on on tabula after 1s
	3. Always Show an icon for actual user location on user location map
	4. Move all icons in category menu down so they start at the bottom of the menu, now there is a black bar on the bottom
	5. if the user location map tiles etc are still loading show some kind of loading animation
	
Index on Tablet and phone
	1. On user location selection, Zoom in so that the actual place name is readable on tablet and phone
	2. User location map and info panel can be made full screen with a button and resizable
	3. User location map:
		1. Increase size of user location map close button, it shall be same size like the info panel close button
		2. Icons on user location map shall have same size, now some icons are smaller
		3. Reduce icon height but keep all fonts the same so remove space between font and border
	4. Increase size of the small full map preview on bottom right by 50%
	5. seems the category icon is larger than the user location map icon, decrease its size to be equal size
	

Index for phone screens:
	1.  Remove text on bottom of user location map "click on map.." 
	2. Zoom in to be able to read the name of selected place
	3. User location map sources info line remove, this is mentioned in about screen

Index for tablet screen ~9-14 inch
	1. Differentiate from mobile screen as there is much more space for better expxerience
	2. Info panel does not need to fit height in landscape, it shall only hold all the content but not be larger than that





60626

index for mobile screens
1) user location map: still the place dots are too small increase by 100% in zoomed in state. zoomed out it is ok
2) in portrait mode the tabula zoom on country selection is not right


please get wiki pages for the segment1 places, user claude ai search. prefered is a wiki of the roman settlement, if not available user the modern place wiki page. 

index for mobile screens only: 
1) seems the tabula zoom level is much too zoomed out, in country mode demo there is hardly the map visible, lets try with zooming in more
2) move legend button to low right on user location map but make sure it does not cover the OSM copyright etc, and set the button to 50% transparency 
3) the selected country text shall be on bottom of user location map not on bottom of window
4) increase dot size in user location map by 100%
5) if i select place on user loc map the tabula zooms in too much, even worse in landscape mode
6) shorten the seg1 text in info panel to just "Place from lost Segment I", the text is a link to the seg1 info panel 



user loc map:
1. leged not fully visible, seems to have a scroll bar, legend shall be on bottom but keep some space to not cover the openstreetmap credentials. in mobile have a legend button only as there is no space
2. segment 1 place selection still not working. if i click on memoriana, it opens cicisa in info panel and tabula pans to it. seems there is something really wrong this happens for many of the places. seems it has something to do with segement info as for boios or brigantium it works fine
3. seems there is no hover info in country mode for the places, shall be country or place depending on mouse location



1. on user location map
a. hover info and clicked info shall be like on tabula with latin, modern, country etc but little bit smaller fonts etc to match the smaller windows size
b. legend shall contain lost tabula segment "category"
c. draw the segment1 routes grey as well 
d. fill the seg1 dots on map with the category color so its clear if its a city or road station etc..
e. the segment 1 selection does not work it jumps to completely weird place, e.g. if i click lucu asturum it jumps to Castra Sour-Ghozlan please analyze and fix



0. please start the server 
1. in case of user location map seg 1 area/place click show the crosshair "outside tabula" on the correct position based on the existing algorithm (predominantly left of map)

2. if segment 1 place is clicked in user loc map, add one sentence of the seg1 info to the info panel. 
3. only show the segment1 info window once but add a link in the one seg1 info sentence to open it again. closing the seg1 info panel does not close the info panel!
4. index: default zoom level for user location map is the whole tabula area, from portugal to india are visible




260625



1\) seg1: dont like the popup for user location map clicked seg1 places, show info panel for these places as well as the seg1 info popup

2\) seg1: populate the wiki pages for these places as well using AI search, you can use claude for that there are tokens avaialble

3\) add the seg1 info also where the modern map loaction data of these places are coming from (omnisviae) to about page.

4\) seems omnisviae places in algeria, eastern half of spain and south west of France, are missing please import let me decide which approach please analyze in detail why this is missing









1\) user loaction map user click: in case of segement 1 place nearby, dont open the info window and select nearest place on tabula. 2) seems there are many seg1 places missing, there are much more in omnisviae, can you load them? provide list first and double check not to overwrite places or add doubles







ok please implement the plan. the info panel on segement on click adds info where these places are from, the Itinerarium provinciarum Antonini Augusti. add wiki link to this and mention the reconstruction of segment 1 places from itinerarium antonini in the about page as well





do you have a copy from tabula-peutingeriana.de, seems the segement 1 places are coming from there? seems omnisviae uses some kind of grey color for segement 1 as well, maybe you can retrieve? https://github.com/renevoorburg/omnesviae/blob/master/public/data/omnesviae.json https://github.com/renevoorburg/omnesviae/tree/master





if about panel is opened, all other windows shall be closed



1\) if i select raetia on user loaction map tabula and info panel open tenedone, please open the selected region place insead 2) in user location map if i select something on segment I, i see it goes to the next place on segment 2 please dont highlight any place and show popup that this is segment 1 which is missing. make the markers from missing segment 1 greyish color  3) add a small legend for the dot colors to the lower right, shall be maximum 1/8 of the user location map window height





1\) for the selected place stronger highlight, lets use RED instead of black 2) the alpha slider shall be in developer menu and save with the save button on bottom of developer menu 3) no other circle markers for roman provinces required, please roll this back,  just the were not selecatble in user location map please fix that and4) i dont see any dots for places in user location map any more, you messed something up?

Optimizations for Index: 

&#x09;	

&#x09;1. DO SEO optimization, update readme etc etc, push new feature experience ancient map with modern technology!!

&#x09;2. Often there are latin names like "Fossa Facta Per Seruos.." where the name is repeated in brackets, please correct that in index

&#x09;3. In index for mouse operation (large screens) add Context information for all buttons

&#x09;4. Places can be selected in country mode if user loc map zoom level allows to select individual places, think about some nice filtering

&#x09;5. In country mode if a place is selected on tabula or user loc map the highlighting is not working pretty well, please highlight stronger like additional frame in black and white?

&#x09;6. Roman provices shall be selectable on user location map

&#x09;7. Add slider to adjust country mode tabula marker transparency fro 0-100

&#x09;8. Info on segment 1: add popup to inform user about missing segment 1 but reconstructed from other documents





22:06:2026





1\) demo: the zoom/pan of the tabula does not go back to very start zoom after user location map is closed 2) for demo use germany as selected country 3) for normal user do not auto select a country when entering country mode





index:

1. demo: country mode: by default names is deactivated so it is more readable
2. in country mode marker opacity is zero as the markers are redrawn in country color as well and the double painting seem too dark.



index on mobile:

1. dots for places on user location map are too large, hard to see anything, need to have different values for large screens and mobile.









index:

1. map preview: maximum height of map preview on bottom right is 1/6 of the window heigt, maximum width 1/2 of screen, remove the black bar on top and bottom a little



2\. demo: when openning category view, city, temple and spa places shall be active and visible on map accordingly



















demo: let me define the timings:

* wait 200ms after about button animation
* animate user loc map and open map after animation is finished
* wait for 1.5s for map to load
* animate country mode button
* activate country mode for 1s
* isolate button animation
* activate isolate mode for 1s
* exit country mode and close user loc map
* animate category button
* open category menu for 1s
* close category button
* end, there shall be all markings NOT active to have plain map



17.6.26



Optimizations for Index:

&#x09;

&#x09;1. Startup demo: animate the user loc map AFTER animating the about button. Then animate the country button wait for 1s and animate again and close the user location map

&#x09;2. Category button active only if country mode is deactivated!

&#x09;

Index for mobile screens:

&#x20;

&#x09;1. Search field font size and result list font size to be reduced by 50%



&#x09;

Optimizations for Index:

&#x09;

&#x09;1. Startup demo: animate the user loc map and country buttons before action open user loc map a little faster

&#x09;2. Category button active only if country mode is deactivated!

&#x09;

Index for mobile screens:

&#x20;

&#x09;1. Increase width but decrease heigh and font size of search field but not to cover the icons on the right

&#x09;2. Landscape mode:

&#x09;	a. increase width of user loc map by 15%, remove my country button and

&#x09;	b.  There is only one button for Names and modern buttons together "names" as there is no space







Optimizations for Index:

&#x09;

&#x09;1. Startup demo make it slower, highlight country button then show effect, toggle again and close window then so user can follow workflow

&#x09;2. Show developer settings highly transparent on bottom right

&#x09;3. Large screens: show category button in case country mode is not active, now it is hidden by user loc map



Index for mobile screens:

&#x20;

&#x09;1. D

&#x09;2. Info window

&#x09;	a. Landscape mode increase width by 20%

&#x09;3. User location map:

&#x09;	a. It is critical to Reduce size of the buttons, not they are too wide and too high, keep icon size and fit but button height and width outline with slight offset around

&#x09;	b. Make sure you analyze in detail and do this

&#x09;4. There is still the weird button on bottom right, please remove see screenshot





Optimizations for Index:

&#x09;

&#x09;1. User loc map: Reduce transparency of places and roads in country mode, add slider to developer mode from 0-100% transparency and save default value persistently in project

&#x09;2. Startup demo, toggle modern countries button to see effect and move back to non country mode so user can try.



Index for mobile screens:

&#x20;

&#x09;1. Decrease size of font and icons in category popup

&#x09;2. Decrease size of buttons, not much icons in user location map, cannot see close button in landscape mode

&#x09;3. Info window

&#x09;	a. Can you reduce the font in info windows map inlay so the "report a problem" and OSM contributors does not hide much of the window?

&#x09;	b. Info popup is in front of the user map

&#x09;	c. Switch info window behavior between portrait and landscape, in portrait shall be bottom full window width, landscape shall be on right side like 1/4 of width height covering top to bottomNPortrait mode:

as

&#x20;

Optimizations for Index:

&#x09;

&#x09;1. Show country mode in demo startup: after openeing the user location map select all countries, isolate is off

&#x09;2. Disable category selection button  in country mode, add the labels buttons to the user location map on the loaction of the category button instead and add button "deactivate country mode" to very bottom left



Index for mobile screens:

&#x09;1. Now user loc map is small enough do not close the user loc map on country or place selection

&#x09;2. Remove the exit country map button on bottom, this is distracting

&#x09;3. Decrease size of buttons in the user loc map, cannot close

&#x09;4. Portrait mode:

&#x09;	a. user loc map full width, height is ok

&#x09;	b. Info panel to 40% screen width, move down by 30% of screen height. In crease height of modern map inlay so the buttom blabla is not covering the loaction

&#x09;5. Landscape mode

&#x09;	a. Increase width of user loc map by 15%, now the modern country button is outside the map

&#x09;	b. Category popup still not reduced in size, it is not visible in total as it going out of screen, shall be 80% of screen height. Please debug in detail why this is not changed yet and you could not fix this!!

&#x09;	c.





Optimizations for Index:

&#x09;

&#x09;1. Show country mode in demo startup: after openeing the user location map select all countries, isolate is off

&#x09;2. Disable category selection button  in country mode, add the labels buttons to the user location map on the loaction of the category button instead and add button "deactivate country mode" to very bottom left



Index for mobile screens:

&#x09;1. Now user loc map is small enough do not close the user loc map on country or place selection

&#x09;2. Remove the exit country map button on bottom, this is distracting

&#x09;3. Portrait mode:

&#x09;	a. user loc map full width, height is ok

&#x09;	b. Info panel to 40% screen width, move down by 30% of screen height. In crease height of modern map inlay so the buttom blabla is not covering the loaction

&#x09;4. Landscape mode

&#x09;	a. Category popup still not reduced in size, it is not visible in total as it going out of screen, shall be 80% of screen height. Please debug in detail why this is not changed yet and you could not fix this!!

&#x09;	b.









Optimizations for Index:

&#x09;

&#x09;1. Use persistent label setting by default labels are off

&#x09;2. By default country mode isolate is off

Index for mobile screens:

&#x09;1. Reduce size of +- buttons

&#x09;2. If country or place is selected close user location window to show the places on tabula

&#x09;3. Info panel in portrait mode on right side. On landscrap mode info panel shall be on bottom third of screen full width

&#x09;4. In portrait mode change country map size to be 40% width and 40% height of screen move it to top of page so it hides the buttons below

&#x09;5. Category popup closes automatically 2s after not changing anything, it does not close on change

&#x09;6. In portrait mode category popup is toooo large, needs to have 70% screen height maximum so scale the content accordingly

&#x09;7. Remove the icon on bottom right dont know what this is for..







Optimizations for Index:

&#x09;

&#x09;1. Draw outline rectangle covering all the palces in country more prominent, make thicker line and use white color additional outline rectangle

&#x09;2. Isolate button deativate activates all categories

&#x09;3. Palästina is missing on user loc map

&#x09;4. Select country in demo mode



Index for mobile screens:

&#x09;- Dont make user loc map fullscreen in protrait, start it below the top row of buttons etc

&#x09;- User loc map in landscrape mode remove "your location" text so buttotons fit screen, reduce size of icons by 30% in user location map

&#x09;- Category popup is far too large, scale by 30% in portrait, 100% in landscape

&#x09;- Category popup close if klicked outside or after 1s automatically as it has no close button





if i activate country mode, only after i move the tabula it shows the markers in country color, also please activate all labels when activating country mode





Optimizations for Index:

&#x09;

&#x09;1. Increase size of user location map button to match width of full screen and +- button conglomerate

&#x09;2. On startup no markings and labels of any category are active

&#x09;3. In country mode

&#x09;	a. Lets try to fill the markings with country color but for sure transparent, otherwiese ist hard to distinguish

&#x09;	b. Active place parker in country mode still transparent, hardly to see! Please debug deeply seems it derives from a dot or road. In non country mode everything is fine

&#x09;	c. Active place marker is too large now in zoomed out mode shall reduce by 40% in radius zoomed out. Zoomed in it is ok







Optimizations for Index:

&#x09;

&#x09;1. Rename "labels" button to "Names", change the icon

&#x09;2. Add another labels button

&#x09;3. Do not have any labels active on startup so user can explore without getting overflown

&#x09;4. Let us think about country mode rework:

&#x09;	a. Isolate country button on top right of user location map below country button if country is active. The checkbox is persistent. Islated country mode is like the current country mode

&#x09;	b. Depending on the button value, if isolate is not active Make all markings on tabula visible and colored in country color so user can see  where the places of each country are located on map

&#x09;	c. User selected country has extra highlight with a big outline frame around all selected country places and each place is highlighted with white frame

&#x09;	d. Change color of user location map outline to show country mode is active

&#x09;5. If country mode is active and user selects place on map the active place marker in user location map ist still transparently displayed and thus barely visible. Shall be non-transparent!

&#x09;



Optimizations for Index:

&#x09;

&#x09;1. User lcoation map zoom much better often something is missing on right side, so zoom out more and pan properly

&#x09;2. Category popup: "label" and "all" buttons still too small, icons inside much too small shall stick into user eyes

&#x09;3. Enrich db entry 1433 with https://tp-online.ku.de/trefferanzeige.php?id=472

&#x09;

&#x09;



Index for mobile screens:

&#x09;- Info panel on the right side, decrease width by 1/4

&#x09;- decrease size of search  field to 1/4 of current size

&#x09;- The tabula peutingeriana is written only on page load animation and animated away to leave just the info (about) icon

&#x09;- User location map full screen in portrait mode, in landscape full height of window,





16.6.26



Optimizations for Index:

&#x09;

&#x09;1. User lcoation map

&#x09;	a. Modern country button incon too small shall be like the places button

&#x09;	b. "Roman Roads" text still in roads button, icon not visible, pelase do deep analysis and check where this is broken

&#x09;	c. Country panning still not working, not zooming out enough and not panning properly to the right so nothing is covered by user locatin map

&#x09;	d. o





Optimizations for Index:

&#x09;



&#x09;1. Country mode hint with exit button places very bad, not easy to find, makes sense to place this near the category button

&#x09;2. User location map

&#x09;	a. The roman roads text is 100% still there in user location map button, please check what is wrong!!!!

&#x09;	b. Further increase icon size by 2/3 to have only small gap to button borders

&#x09;	c. Seems in country mode i cannot select places on the tabula map any more this is needs fix.

&#x09;	d. Zoom/pan tabula map on country selected does not work at all.

&#x09;		i. For some countries it works better for some worse main issue here is the user location map covers some of the area like for algeria, and most others just a little like 15% zoom out required and little pan to right

&#x09;		ii. Big problem is italy, there is 50% off screen of the 50 on tabula screen 2/3 is behind user location window

&#x09;			1) Please do deep analysis what is going on and look for more possible root causes. Explain them to me and present options to fix

&#x09;			2) n





Optimizations for Index:

&#x09;



&#x09;1. If i select country in user location map dropdown it does not pan/zoom to the country in user location map

&#x09;2. User location map:

&#x09;	a. Remove name from "roman roads" button show icon only like for place buttton

&#x09;	b. Icons shall be larger, fill mostly the button space to be well visible

&#x09;	c. Still click on italy e.g. does not work zoomed out as i open the place info instad selecting the country see screenshot

&#x09;	d. If i click a country e.g. italy here, Panning the tabula map to the right position does not work for italy, seems 50% of italy is still out of screen

&#x09;	e. The ringed marker is now larger but very much transparent had to see, check screenshot as well

&#x09;	f. n

&#x09;



Index for mobile screens:

&#x09;1) Check the old UI in old version on GH like 2 wks ago. How can i see the old version is it possible to view the index on the old version?

&#x09;2) n





Optimizations for Index:

&#x09;

&#x09;1) +- buttons on top of each other, remove home button

&#x09;2) Full screen button has height of + and - together

&#x09;3) Category popup all and labels button need to be increased in size to house the icon, now it looks overflown, font increased as well a little

&#x09;4) Locate popup buttons are a mess now. Country mode button should have label "Modern Countries" remove text from roads button

&#x09;5) Panning to right loaction for country very bad still have a screenshot attached for italy. Please forget all pc/py, there is not stitched mode only miller large calibrated tabula!!

&#x09;6) Place selection in country mode: do not see any highlight in user location map if select place on tabula fix made it worse, hardly can see the white ring around the place looks transparent like the other roads and dots on the user location map

&#x09;7) Search result panning not working: first result is off. If i search the same place a 2nd time it pans right!



Optimizations for Index:

&#x09;

&#x09;1) Put +-home buttons right of the full screen button

&#x09;2) Email button on top right same height like the about button.

&#x09;3) About button text shall be the i icon and text "The Tabula Peutingeriana"

&#x09;4) Emphasize "all" and "labels" buttons in category popup by among others:

&#x09;	a. add icons to them to make more clear what they imply

&#x09;	b. add hover info to explain to user

&#x09;5) In user location window: remove text from the icons, make icons much larger, add hover info

&#x09;6) User location countryy mode: seems like if i click in country where there is aplace i cannot select the country, fix

&#x09;7) In country mode if user selects place on tabula the country selection highlight in user location map shall not be reduced transparency so it is better visible..

&#x09;8) It takes some tries with search palces to get to the right place, seems very buggy. After seaching a place several times it seems to repair

&#x09;9) n

&#x09;

Index for mobile screens:

&#x09;1) Mobile is a fucking mess,

&#x09;	a. cant close the category popup

&#x09;	b. Cannot close the user map as the top buttons are too large spanning over the screen. Use icons only in mobile screens

&#x09;	c. Too many buttons now

&#x09;	d. Can you back to like 2 weeks ago on github manybe to old ui and work out a design based on this one and have the ckeckbox on bottom right to switch to new design and back?

&#x09;	e. n

&#x20;

**Optimizations for Index:**

&#x09;

&#x09;**1) I have calibrated and changed a lot again, please commit to make permanent**

&#x09;**2) Need to tune labels more, no max label font size for desktop selectable e.g.. can you move developer settings button to bottom right of index, not in about any more and optimize the algorithm, now the different sliders are confusing for the user. Think of some options and let me decide**

&#x09;**3) No crosshair needed if place is selected exactly or very close (5km was limit?)**

&#x09;**4) Country mode: on selected no cross hairs needed!**

&#x09;**5) Add info/feedback email button with mail logo on button to info@three-mills.com  below "about" button**

&#x09;**6) Fullscreen button shall be larger, put it to the very top left**

&#x09;**7) Zoom pan tabula to all selected country places in view does not work, please review en detail and come up with optimization options for me to decide.**

&#x09;**8) Country mode needs to be emphasized. What do you suggest to exit country mode? Let me decide to implement with options or no change**

&#x09;**9) Lets change the user location buttons: places, roads can be shown nicely by icons, do you have a nice icon for countries? Lets try**

&#x09;**10) n**

&#x09;

**Index for mobile screens:**

&#x09;**1) Lets optimize for mobile UI. Can you go back to the old layout for mobile so i can check? Currently it is unusable for mobile screens very bad maybe lets have a little checkbox to change back and forth from the layouts in mobile screens for me to see what is possible**

&#x09;**2)**





15.6.26

Optimizations for Index:



&#x09;1) Add "name labels" button on category popup

&#x09;2) On Country selected tabula map and places changes:

&#x09;	a. Zoom/pan on country selection is better bot not there yet, not all of the country is visible on map as something is hidden behind the user map, pan and zoom so that everything is visible on the right side of the user map.

&#x09;	b. increase the width of the rectangle in country color around all places by 100%

&#x09;	c. There is no country outline of the individual places, please try to add that to make more clear that this place belongs to the selected country

&#x09;3) Do SEO optimization, push the new features especially like "see your country on the ancient map!" also rework readme, about panel etc with the new features

&#x09;

Index for mobile screens:

&#x09;1) Lets optimize for mobile UI. Can you go back to the old layout for mobile so i can check? Currently it is unusable for mobile screens very bad maybe lets have a little checkbox to change back and forth from the layouts in mobile screens for me to see what is possible









Optimizations for Index:

&#x09;1) Do not deactivate user location map on coutry selection, just pan/zoom the tabula in backgroudn the right way to make sure all places of this country are in view for the user

&#x09;2) Niger and mali are not in country map in user location map, why is that? There is #3657 which covers both countries?

&#x09;3) Latin Translations ofter very bad, e.g. aerae fines romanum, or Flumen quidam Grin.. Or "Salinae inmensae quae cum luna crescunt et decrescunt", Arhasarto siluesa.. . In contrast gemini gives much better results, can you try google ai search or better model from claude? Do only the sentences with more than three latin words (not counting anything after a special letter like "(" or "\[" etc) please provide some options

4\) Latin translation in hover info  and info panel for places as well, this might be interesting for "normal" user! Have it in smaller font italic. In info panel if latin name is longer than three words show the translation in smaller font as well below the latin title, below is modern name



15.6.26





Optimizations for Index:

&#x09;1. Seems wikipedia search does not work fine, pleasea hardcode ulm link in Database if i give it to you

&#x09;	a. Norico https://de.wikipedia.org/wiki/Noricum see Barrington Atlas info from ulm ulm page: Noricum (19 E3)

&#x09;	b. Belgica is fucking no-go

&#x09;	c. Roma shall be rome city not rome search in wiki https://en.wikipedia.org/wiki/Rome

&#x09;	d. 3000667 wiki shall be https://en.wikipedia.org/wiki/Suvaja\_(Kozarska\_Dubica)

&#x09;	e. Europus/europos https://en.wikipedia.org/wiki/Euromus

&#x09;

Changes in Database editor

&#x09;1) Derive empty countries with geocoding and from tabula-peutingeriana.de

&#x09;2) hover over wiki link opens preview with button to go to this page





Database refinement:

&#x09;1) Refine geolocation of all not geolocated yet entries: if there is no geolocation check ulm link to pleiades page which often has  a geolocation, please ask me if you have any trouble

&#x09;2) retrieve country from geolocation using web or other tools. Geolocation place can be retrieved as well to be used for wikipedia link search. If you have issues ask me for help









Optimizations for Index:

&#x09;1. Seems wikipedia search does not work fine,

&#x09;	a. For regions, preferably look for latin name sometimes helps like for capania, modern name seems german which does not give result for english wikipedia

&#x09;	b. Italia wiki link does not work as well shall be https://en.wikipedia.org/wiki/Roman\_Italy

&#x09;2. Can you add the first paragraph of wikipedia in onclick info panel below modern name to give some explanation













Optimizations for Index:

&#x09;1. Seems wikipedia search does not work fine,

&#x09;	a. for burno it shall be https://en.wikipedia.org/wiki/Ivo%C5%A1evci, if there are keywords like "bei" or "near" then use the word before that

&#x09;	b. For people, look e.g. in case of Sauromatum shall be https://en.wikipedia.org/wiki/Sarmatians delivered by google search "SARMATEVAGI people wiki"

&#x09;	c. For regions e.g. provincia africa shall be https://en.wikipedia.org/wiki/Africa\_(Roman\_province), here the V shall not be replaced with u, try both to find something useful. Web search for latin name roman province gives good result as well



















Optimizations for Index:

&#x09;1. Tabula info panel shall be shown centered horizontally and vertically, make it 100% wider on large screens

&#x09;2. Remove roman province category button

&#x09;3. Rename regions/people button to "roman regions/provinces/people"

&#x09;4. Seems wikipedia search does not work fine, for lvgdvnensis shall be Lugdunensis with the v to u change, could you implement something to check if this helps? Try the Latin Std field if latin name fails?

&#x09;5. Regions cannot be hovered in normal map mode,  lets try to have to hover info work in the background of the other markings even if the regions are not active i will tell you if it does not work

&#x09;







Optimizations for Index:

&#x09;1. Move the label settings button to the tabula info panel bottom so its more hidden to custom users.

&#x09;2. Dont show modern map preview if there is no geolocation like for belgica

&#x09;3. Discuss with me how to handle for example the regions without modern name, there shall be wikipedia link to them









Optimizations for Index:

&#x09;1. Tabula information panel shall be much bigger and shown centered on the window

&#x09;2. Regions\&/people marking transparency shall be similar to the other marking transparency now ist hardly visible

&#x09;3. Startup zoom does not work, pelase fix

&#x09;4. The language buttons in "tabula info panel" shall translate all text on in the tabula info panel as well, same for the category labels etc

&#x09;5. The onclick info panel, wikipedia and ulm link fonts shall be larger

&#x09;6. In onclick info panel: plz write out the country code as some ar not easy to guess

Onclick info panel: write "Original Tabula Peutingeriana view" between OSM preview and ulm preview so ist clear..







Optimizations for Index:

1\. I cannot find burno hover info, seems its covered with libvrina in index. Please have very hard order, regions/people markings  are always in background, cities etc roadstations on front

2\. On click marking Info panel:

&#x09;a. Wikipedia and ulm link shall be above the map under the category, not on top

&#x09;b. The language selection (dropdown maybe better) shall be in the general tabula inforamtion pnael opens with the information button  not in the click marking info panel

3\. The startup zoom does not work, shall be like in the screenshot, rome in center and zoom so that the height of the map fits the window height which is like if i klick a segment. On startup the info panel shall be opened to explain the map a little and language can be selected



















Optimizations for Index:

&#x09;1. Klick outside of the information window closes the information window

&#x09;2. In browser/large screens show the ulm preview below the map. Klick on ulm preview opens link to ulm page in new tab

&#x09;3. Rename regions button to "regions/people" and toggle people as well with the button so there is a separate view of regions/people on map

&#x09;4. Could you identify the system language and translate the info page for the relevant country? Have a button select language on the info panel to change language between german, english and system language.

&#x09;5. The startup zoom/focus does not work, rome needs to be at center exactly between segement 5 and 6, zoom in so the map height fits the screen height

&#x09;6. Ulm and wikipedia links shall be above the map, font size shall be size similar to the rest information

&#x09;7. If there is no geolocation, no map shall be shown





















Optimizations for Index:

&#x09;1. Klick outside of the information window closes this

&#x09;2. Region  button is on the bottom of all the other category buttons on the very left side

&#x09;3. On start, rome in the middle (between segment 5 and 6) so that the map fills vertically the screen

&#x09;4. Order of markings: region in very background, then people, mountains, waters lakes etc then all the others on top. Important is that smaller markings are always on top of the larger ones

&#x09;5. Hover info over the segment buttons shows the segment info like e.g. III: III - Germania Gallia Luguria etc

&#x09;6. Info panel:

&#x09;	a. There shall be no tabula detail, this was for calibrate only.

&#x09;	b. If there is no geolocation, no map shall be shown like

&#x09;	c. Wikipedia link and ulm DB link are an top of the map, segment  info as well. Latin and modern name are similar size and font as both are equally important



















Optimizations for Index:

1\. Separate region/province buttons as they overlay too much, region button toggles only region markings/names and deactivates all other markings if on.

2\. Legend does not have any use as the category toggles have the right color, please remove. Add an button which opens a extensive info panel with movitating and intersting information about the tabula peutingerina and links to wikipedia, video etc.















calibrate

1\) the current buttons water and region shall toggle the visibility on the map.. show them on map, now they do not seem to have any effect

2\) add filter button for region and water category to calibrate them, this is missing so i cannot select them on map



















1\. Check DB: if there is no tabula segement--> derive from Ulm if available with segment +1 correction from ulm for sure

2\. Check for each db entry with ulm segment info available that there is a tabula segement with +1, correct if not

3\. All the segment I seem to be labeled segment II? All segement I places are available here https://www.tabula-peutingeriana.de/list.html?segm=0. Please not that the sement I is lost so all these places cannot have markings on the miller



DB editor:

1\. Add button to show empty only for each row

2\. add button for each line to edit the db entry similar to calibrate. delete entry should be double confirmed by the user























Calibrate

1\) I want to have a button to delete a marking and edit button to manually change properties of the DB entry  or delete entry totally from DB. Please make a backup of the DB with todays date

2\) Why no ulm preview for many entries like https://tp-online.ku.de/trefferanzeige.php?id=2105



DAtabase

1\) roman provices/regions and preople DB entries do not have a segment, info is easily available from ulm and tabula pages. please enrich ulm and DB/tabula location info. data is avalable here https://www.tabula-peutingeriana.de/list.html?typ=reg and https://www.tabula-peutingeriana.de/list.html?typ=gen as well as in the ulm DB pages























Optimizations for Index:

1\) Optimize info panel click opening, if panning or click too long like >1s dont open info window on mouse release

2\) Fullscreen mode should have all the features like in normal mode

















1\) missing https://tp-online.ku.de/trefferanzeige.php?id=1953, https://tp-online.ku.de/trefferanzeige.php?id=1956, https://tp-online.ku.de/trefferanzeige.php?id=2885, https://tp-online.ku.de/trefferanzeige.php?id=1274, https://tp-online.ku.de/trefferanzeige.php?id=1379, https://tp-online.ku.de/trefferanzeige.php?id=1559, https://tp-online.ku.de/trefferanzeige.php?id=1694, https://tp-online.ku.de/trefferanzeige.php?id=1717, https://tp-online.ku.de/trefferanzeige.php?id=2015

2\) 3002456, 2783, 3002469, 3002476, 2862 and many more cannot be shown in calibrate, why?





1\) please add a button in calubrate to load recently added/modified entries only

1\) missing dB entries:  https://tp-online.ku.de/trefferanzeige.php?id=1887, https://tp-online.ku.de/trefferanzeige.php?id=2152, https://tp-online.ku.de/trefferanzeige.php?id=667, https://tp-online.ku.de/trefferanzeige.php?id=685, https://tp-online.ku.de/trefferanzeige.php?id=749, https://tp-online.ku.de/trefferanzeige.php?id=769, https://tp-online.ku.de/trefferanzeige.php?id=446, https://tp-online.ku.de/trefferanzeige.php?id=538, https://tp-online.ku.de/trefferanzeige.php?id=2182, https://tp-online.ku.de/trefferanzeige.php?id=1904, https://tp-online.ku.de/trefferanzeige.php?id=510, https://tp-online.ku.de/trefferanzeige.php?id=149, https://tp-online.ku.de/trefferanzeige.php?id=995, https://tp-online.ku.de/trefferanzeige.php?id=836, https://tp-online.ku.de/trefferanzeige.php?id=943, https://tp-online.ku.de/trefferanzeige.php?id=1016, https://tp-online.ku.de/trefferanzeige.php?id=1007, https://tp-online.ku.de/trefferanzeige.php?id=1137, https://tp-online.ku.de/trefferanzeige.php?id=2501, https://tp-online.ku.de/trefferanzeige.php?id=1953, https://tp-online.ku.de/trefferanzeige.php?id=3467

3\) 3002233 water

4\) stored and new marker coordingates shall be in one line not on top of each other

5\) enrich #1816 with https://tp-online.ku.de/trefferanzeige.php?id=891 which is ulm

6\) cannot see 2804 in calibrate but in DB





















1\) Latin Name too short for #3003470 update from ulm page

2\) Missing entries:  https://tp-online.ku.de/trefferanzeige.php?id=53, https://tp-online.ku.de/trefferanzeige.php?id=1347, https://tp-online.ku.de/trefferanzeige.php?id=1358, https://tp-online.ku.de/trefferanzeige.php?id=1380, https://tp-online.ku.de/trefferanzeige.php?id=265































2\. Ndesina --> spa

3\. Missing DB entries to add/load with ulm links: https://tp-online.ku.de/trefferanzeige.php?id=3470, https://tp-online.ku.de/trefferanzeige.php?id=1441, https://tp-online.ku.de/trefferanzeige.php?id=1712, https://tp-online.ku.de/trefferanzeige.php?id=1717, https://tp-online.ku.de/trefferanzeige.php?id=1207









1\) Optimizations for Index: Search does not work really, cannot find most places

2\) Calibrate: I want to have a button to delete a marking and edit button to manually change properties of the DB entry  or delete entry totally from DB. Please make a backup of the DB with todays date











Optimizations for Index:

1\) If there is no modern place do not show map in info panel

2\) Index starts up zoomed fully out, if i click segment, it does not pan/zoom to the right one











1\. So many places with ulm DB number but no preview like 3555

2\) seems there are many entries which have same data id like silamalasso and \[lacus musiris], actually i find from 2476 to 2481 are all double. this does not work! what do you propose to do? please check all DB entries for doubles in DB ID









1\. Add Ulm location to DB for all entries this enables double checking

2\. 1125 --> stadt





1\. 211 --> region

2\. 2948 --> island

3\. 1310 --> lake

4\. 242 --> spa

5\. asiLe˙sva· ADaQvas· Mil· XIX· --> spa

6\. Everything with island in latin name is type island!

7\. Everything with "doppelturm" shall be city!

8\. Hasta missing in calibrate but in DB 1117

9\. Aqvileia not city but road station, --> check all city entries in DB: if there is no symbol it shall be a road station

10\. https://tp-online.ku.de/trefferanzeige.php?id=923 missing in DB

Enrich #1768, #2456 with ulm info, but take care. Ulm DB segment location is shifted by -1 due to not considering the missing segment 1











calibrate:

1\) show places without modern, no lat/lng, and no tabula\_segment as well, let me find it.

2\) add ulm segment location info next to the database segement location in info panel

3\) even places without modern, no lat/lng, no tabula\_segment are visible in calibrate list









Optimizations for Index:

1\. Add ulm to data sources

2\. Klick on map does not zoom

3\. Reduce with of info onclick popup

4\. Label settings: add marking transparency slider

5\. By default on startup, city, temple and spa category are selected, the toggle all button shall be smaller as it leads to overflow..

6\. Decrease with of onclick info panel by 20%

7\. Klick on map does not zoom

8\. Still the bug: on first load the label fonts are too large and snap back with first move.

9\. Toggle labels and markings idependently!









all for calibrate only:

1\. Country flag next to country like in index

2\. Latin text and ulm map preview  are shown 100px away from mouse pointer on map to more easy find the place

3\. Next item in list not working with filter sometimes









&#x09;DB update:

&#x09;3. Missing https://tp-online.ku.de/trefferanzeige.php?id=922

&#x09;4. Enrich Fons with https://tp-online.ku.de/trefferanzeige.php?id=1135

&#x09;5. Entry 1741,1400 is spa type

&#x09;6. 2934,1693 city --> check if symbol type "a" then it must be a city or major city, please check DB

&#x09;7. 2150 location wrong= 10b1  check ULM DB

&#x09;8. Presidio Silvani is a road station not a temple!

&#x09;10. FL u artum falsch

&#x09;11. merge city and "major city" and City category, update calibrate and index with the city update

&#x09;12. Iovis penninus, Iovis Tifatinus segment wrong, not transformed from ulm to DB?

&#x09;13. Sankt peter tempel?

&#x09;14. Everything with "port" in beginning of latin name shall be port category

&#x09;15. missing https://tp-online.ku.de/trefferanzeige.php?id=2517

&#x09;































optimize index.html:

1)Hover info a little bit further away not to hide the marking

2\) Mobile Info Panel all ON Page left of map

3\) On start to big fonts for markings

4\) Mobile: open info window only on click for<1s otherwise scrolling opens the info pop-up

5\) on markings modern names are sometimes toooo long, should be one like four words maximum on the map markings

6\) category on info panel should be much larger font and add an icon so its more distinguishable

7\) County flag not visible in info panel in large screen browser

8\) increase size of the font for country in info panel and in crease the size of the flag as well

9\) Rename button "Select all" --> hide/show all

10\) Select all/labels, categories buttons overlap slightly, move apart































&#x09;- Can you thoroughly match every DB entry to  match to a page on ulm, many DB entries seem to have the same ulm link most dont have one yet. Please use a good plausibilization algorithm:

&#x09;	○ Modern name

&#x09;	○ Latin name (often letter v in the names in DB is u letter in ulm please take care of that in the match searching algorithm)

&#x09;	○ Tabula location = "Planquadrat" in ulm (please note that ulm segment is shifted by -1 compared to DB) the tabula peutingeriana nomenclature is the master here as there is a missing 1st segement.

&#x09;	○ You can use ulm DB with all entries here "C:\\Users\\sknue\\OneDrive\\Desktop\\Proj\\tabula-peutingeriana\\Ulm Database\\Tabula Peutingeriana.htm" but beware: many entries are double you need to check which one is the right one!!

&#x09;	○ Create some kind of confidence so i can double check

&#x09;	○ create a separate DB with all ulm pages and data from the pages first to work with that please create a viewer for this new DB as well, later we might use some to the main DB

&#x09;		§ Ulm DB ID (in link)

&#x09;		§ Latin name

&#x09;		§ Modern name

&#x09;		§ Planquadrat

&#x09;		§ Großraum

&#x09;		§ Typonym Typus

&#x09;		§ Farbe des Typonyms

&#x09;		§ Vignette Typus

&#x09;		§ Wikipedia link

&#x09;		§ Datierung des Typonyms









ok the remaining low are missing in DB. please make sure the DB nomenclature tabula loaction is ensured.

1\) can you enrich the high/medium matches DB with the ulm information,

&#x09;a) if there is modern location in Ulm DB please overwrite the current DB value.

&#x09;b) if there is name mismatch in latin, please take over the Ulm value

&#x09;c)  please make sure the Ulm ID is written to DB ulm ID column correctly, now there are often wrong values in DB which should be overwritten



2\) add all low matches as new entries to the DB.

3\) import the vignette type as well for all Entries

