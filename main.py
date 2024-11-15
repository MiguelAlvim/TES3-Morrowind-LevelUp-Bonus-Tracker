import platform
import os
import sys
import FreeSimpleGUI as g
from AttributesAndSkills import attributesAndSkills as attributes, skill, attribute
from ReadOpenMWRamOnWindows import GetOpenMWProcessHandle, CloserocessHandle, GetOpenMWCurrentLeveUpBonuses, OpenMWCharcterLevelUpTotalSkills

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
pointsGainedThisLevel:dict[str,int] = {}
modifiersGainedThisLevel:dict[str,int] = {}

#STAR GUI creation
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
	modifiersGainedThisLevel[atrib.name] = 0
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
			pointsGainedThisLevel[ski.name] = 0
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
		modifiersGainedThisLevel[atrib.name] = 0
		if len(atrib.skills)>0:
			windowObjectArray[f'mf_{atrib.name}'].update(f"+1")
			windowObjectArray[f'tot_{atrib.name}'].update(f"(0)")
		for ski in atrib.skills:
			windowObjectArray[f'vl_{ski.name}'].update(f"0")

def updateGuiAndSkillValues(windowObjectArray, checkResult):
	"""Receives and array with the objects of the window and the result of the function actionToExecute from a buttonEvent object and update the GUI and internal values if necessary
	"""
	if checkResult != None:
		currentVal = pointsGainedThisLevel[checkResult[0]]
		newVal = currentVal + checkResult[2]
		if newVal >= 0 and newVal <=99:
			#skill counter
			pointsGainedThisLevel[checkResult[0]] = newVal
			windowObjectArray[f'vl_{result[0]}'].update(newVal) 
			#attribute modifier counter
			modifiersGainedThisLevel[checkResult[1]] += newVal - currentVal			
			windowObjectArray[f'tot_{result[1]}'].update(f"({modifiersGainedThisLevel[checkResult[1]]})") 
			#checking final atribute modifier, based on the data in https://en.uesp.net/wiki/Morrowind:Level
			finalModifer = 0
			if modifiersGainedThisLevel[checkResult[1]]<=0:
				finalModifer = 1
			elif modifiersGainedThisLevel[checkResult[1]]<=4:
				finalModifer = 2
			elif modifiersGainedThisLevel[checkResult[1]]<=7:
				finalModifer = 3
			elif modifiersGainedThisLevel[checkResult[1]]<=9:
				finalModifer = 4
			elif modifiersGainedThisLevel[checkResult[1]]>=10:
				finalModifer = 5
			windowObjectArray[f'mf_{result[1]}'].update(f"+{finalModifer}") 

#GUI loop and event handling
while True:
	event, values = window.read()
	if event == g.WIN_CLOSED or event == "Cancel":
		break
	

	#Manual Button Events
	if event.startswith('mb_') or event.startswith('pb_'):
		for evnt in eventList:
			result = evnt.actionToExecute(event)
			if result != None:
				updateGuiAndSkillValues(window,result)
	if event == 'btt_clear':
		clearScreen(window)

window.close()