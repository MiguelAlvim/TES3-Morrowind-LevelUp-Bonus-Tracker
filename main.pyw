import platform
import os
import sys
import FreeSimpleGUI as g
from AttributesAndSkills import attributesAndSkills as attributes
from ReadOpenMWRamOnWinAndLinux import GetOpenMWWindowProcess, GetCharacterSkillsIncreases, OpenMWCharcterLevelUpTotalSkills

#Global Flags
isOpenMWRamReadingOn = False
openMWProcess = None

#This Class has all we need to handle a minus or plus event
class buttonEvent:
	"""Represents an custom event to be trigged by the plus and minus buttons of the screen
	"""
	def __init__(self,id:str,skillname:str,attributename:str,modifyValue:int):
		"""
		:param id Screen object ID
		:param skillname Name of the skill that the buttons modifies. Used to determine which field to modify
		:param attributename Name of the attribute that the buttons modifies. Used to determine which field to modify
		:param modifyValue Value to be added to the total of the attribute if the button is pressed
		"""
		self.id:str = id
		self.skillname:str = skillname
		self.attributename:str = attributename
		self.modifyValue:int = modifyValue

	def actionToExecute(self,id:str):
		"""Checks to see if the event ID passed is the one soted on this object.
			Returns None if it's not the correct ID; A tuple with the name of the field, it's attribute and the value to be incremented to it otherwise
		:param id String containing the detected event
		
		"""
		if id == self.id:
			return (f'{self.skillname}',self.attributename,self.modifyValue)
		return None


#List of Event IDs and what to Do with them
eventList:list[buttonEvent] = []

#Global Variables used on Manual Tracking
pointsGainedThisLevelManual:dict[str,int] = {}
modifiersGainedThisLevelManual:dict[str,int] = {}

#Global Variables used on Automatica RAM reading mode
pointsGainedThisLevelAutomatic:dict[str,int] = {}
modifiersGainedThisLevelAutomatic:dict[str,int] = {}

#START GUI creation
layoutLeft = [[g.Push(),g.Text("Skills Raised on Current Level", font='bold'),g.Push()]]
layoutLeft.append([g.HorizontalSeparator()])
#To homogenize the space between skills, we will create padding for attributes that lack this amount of skills
largestListElementSize = len(max(attributes).skills)
#By default the GUI LIB add a padding of 3 pixels up and 3 pixels down, 
#therefore each element bellow 'largestListElementSize' will require 6 pixel in the y axis to be added at the end of the attribute skill list
#The largest element used on each row is a button, whose default size is 26 pixels
#Therefore, the size per element missing has to be 26+6 = 32 pixels on the y axis
paddingPerElementMissing = 32

totalPerColumn = 3
elementOnColumnCounter = 0
colunms = []
colunm = []
finalLayout = []
for atrib in attributes:
	modifiersGainedThisLevelManual[atrib.name] = 0
	if len(atrib.skills)>0:
		colunm.append([g.Text(atrib.name, font='bold', p=((0,0),(3,3))),g.Text("(0)",font='bold',key=f'tot_{atrib.name}',p=((0,0),(3,3)))])
		for ski in atrib.skills:
			colunm.append(
				[
				g.Button(button_text="-", key=f'mb_{ski.name}', enable_events= True),
				g.InputText(size=(3,1),   key=f'vl_{ski.name}', disabled=True, default_text='0', justification='center'),
				g.Button(button_text="+", key=f'pb_{ski.name}', enable_events= True),
				g.Text(ski.name)
				]
			)
			eventList.append(buttonEvent(id=f'mb_{ski.name}',modifyValue=-1,skillname=ski.name, attributename=atrib.name))
			eventList.append(buttonEvent(id=f'pb_{ski.name}',modifyValue=1,skillname=ski.name, attributename=atrib.name))
			pointsGainedThisLevelManual[ski.name] = 0
		for a in range(len(atrib.skills),largestListElementSize):#Adding the necessat padding for an aligned UI
			colunm.append([g.Sizer(0,paddingPerElementMissing)])
		colunm.append([g.HorizontalSeparator()])

		elementOnColumnCounter += 1
	if elementOnColumnCounter >= totalPerColumn or atrib == attributes[-1]:
		elementOnColumnCounter = 0
		colunms.append(colunm)
		colunm = []

for col in colunms:
	finalLayout.append(g.Column(col,vertical_alignment='top'))
layoutLeft.append(finalLayout)

layoutRight = [[g.Push(),g.Text("Expected Bonuses on Next Level Up", font='bold'),g.Push()]]
layoutRight.append([g.HorizontalSeparator()])
for atrib in attributes:
	layoutRight.append([g.Text("+1", key=f"mf_{atrib.name}"),g.Text(atrib.name, font='bold')])
layoutRight.append([g.HorizontalSeparator()])
layoutRight.append([g.Button(button_text="Clear", key=f'btt_clear', enable_events= True)])

#Direct RAM read is currently only avaible on Windows
layoutRight.append([g.Text("Read from Running OpenMW (Only on Windows)")])
layoutRight.append([g.Button(button_text="OFF", key=f'btt_toggleOpenMWRAM', enable_events= True, button_color = "red"), g.Text("Updates Every 0.5s")])

#selecting icon type - On windows must be .ico, on linux must not be icon
icon = os.path.dirname(os.path.realpath(sys.argv[0]))+"\icon.ico"
if platform.system() == "Linux":
	icon = os.path.dirname(os.path.realpath(sys.argv[0]))+"\icon.png"

window = g.Window("TES 3:Morrowind Level Up Bonus Tracker",
	[[g.Column(layoutLeft,vertical_alignment='top'),g.VerticalSeparator(),g.Column(layoutRight,vertical_alignment='top')]],
	icon=os.path.dirname(os.path.realpath(sys.argv[0]))+".\icon.ico"
	)
#END GUI creation

def clearScreen(windowObjectArray):
	"""Clears all the skills declared an the modifiers presented	
	"""
	for atrib in attributes:
		modifiersGainedThisLevelManual[atrib.name] = 0
		if len(atrib.skills)>0:
			windowObjectArray[f'mf_{atrib.name}'].update(f"+1")
			windowObjectArray[f'tot_{atrib.name}'].update(f"(0)")
		for ski in atrib.skills:
			windowObjectArray[f'vl_{ski.name}'].update(f"0")

def updateModifiersGainedThisLevel(characterFromRam:OpenMWCharcterLevelUpTotalSkills):
	"""Receives an entire set of a character attributes (probaly from RAM direct access) and updates the app internal tracking with them

	USED ON AUTOMATIC MODE
	"""
	if characterFromRam != None:
		#Level Up Bonuses and Total of raised Skills:
		for attrib in characterFromRam.AmountSkillRaised:
			modifiersGainedThisLevelAutomatic[attrib] = characterFromRam.AmountSkillRaised[attrib]

def updateGuiAndSkillValues(windowObjectArray, checkResult:tuple[str,str,int]):
	"""Receives and array with the objects of the window and the result of the function actionToExecute from a buttonEvent object and update the GUI and internal values if necessary

	USED ON MANUAL MODE
	"""
	if checkResult != None:
		currentVal = pointsGainedThisLevelManual[checkResult[0]]
		newVal = currentVal + checkResult[2]
		if newVal >= 0 and newVal <=99:
			#skill counter
			pointsGainedThisLevelManual[checkResult[0]] = newVal
			windowObjectArray[f'vl_{result[0]}'].update(newVal) 
			#attribute modifier counter
			modifiersGainedThisLevelManual[checkResult[1]] += newVal - currentVal			
			windowObjectArray[f'tot_{result[1]}'].update(f"({modifiersGainedThisLevelManual[checkResult[1]]})") 
			#checking final attribute modifier, based on the data in https://en.uesp.net/wiki/Morrowind:Level
			finalModifer = 0
			if modifiersGainedThisLevelManual[checkResult[1]]<=0:
				finalModifer = 1
			elif modifiersGainedThisLevelManual[checkResult[1]]<=4:
				finalModifer = 2
			elif modifiersGainedThisLevelManual[checkResult[1]]<=7:
				finalModifer = 3
			elif modifiersGainedThisLevelManual[checkResult[1]]<=9:
				finalModifer = 4
			elif modifiersGainedThisLevelManual[checkResult[1]]>=10:
				finalModifer = 5
			windowObjectArray[f'mf_{result[1]}'].update(f"+{finalModifer}") 

def updateWindowWithModifersGainedThisLevel(windowObjectArray, modifierDict = pointsGainedThisLevelManual):
	"""
	Updates the final level up modifiers based on the passed dictionary 

	Default dict is the Manual one
	"""
	for modifer in modifierDict:
		finalModifer = 0
		if modifierDict[modifer]<=0:
			finalModifer = 1
		elif modifierDict[modifer]<=4:
			finalModifer = 2
		elif modifierDict[modifer]<=7:
			finalModifer = 3
		elif modifierDict[modifer]<=9:
			finalModifer = 4
		elif modifierDict[modifer]>=10:
			finalModifer = 5
		windowObjectArray[f'mf_{modifer}'].update(f"+{finalModifer}")		

def EnableOrDisableManualControls():
	pass

#GUI loop, event handling and RAM reading
while True:
	event, values = window.read(timeout=500)
	if event == g.WIN_CLOSED or event == "Cancel":
		if openMWProcess == None:
			openMWProcess.close()
		break

	#OpenMW RAM Reading	
	if isOpenMWRamReadingOn:
		if(openMWProcess == None):
			openMWProcess = GetOpenMWWindowProcess()
		if(openMWProcess != None):
			char = GetCharacterSkillsIncreases(openMWProcess)
			print(char)
			updateModifiersGainedThisLevel(char)
			updateWindowWithModifersGainedThisLevel(window,modifiersGainedThisLevelAutomatic)
	
	#Button Events
	if (event.startswith('mb_') or event.startswith('pb_')) and not isOpenMWRamReadingOn:
		for evnt in eventList:
			result = evnt.actionToExecute(event)
			if result != None:
				updateGuiAndSkillValues(window,result)
	if event == 'btt_clear':
		clearScreen(window)
	if event == 'btt_toggleOpenMWRAM':
		isOpenMWRamReadingOn = not isOpenMWRamReadingOn
		EnableOrDisableManualControls()
		if isOpenMWRamReadingOn:
			window['btt_toggleOpenMWRAM'].update("ON")
			window['btt_toggleOpenMWRAM'].update(button_color = "green")
		else:
			window['btt_toggleOpenMWRAM'].update("OFF")
			window['btt_toggleOpenMWRAM'].update(button_color = "red")
			updateWindowWithModifersGainedThisLevel(window,modifiersGainedThisLevelManual)

window.close()