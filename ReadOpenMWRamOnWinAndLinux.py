import PyMemoryEditor, sys, ctypes
from io import StringIO

#Base Class for return
class OpenMWCharcterLevelUpTotalSkills:
	"""
	Holds the total of skills of each attribute that have been leved up on the current level, as well as current skill and attribute levels
	"""
	def __init__(self):
		#Atributtes
		self.Attributes = {}
		self.Attributes['Strength'] = 0
		self.Attributes['Intelligence'] = 0
		self.Attributes['Willpower'] = 0
		self.Attributes['Agility'] = 0
		self.Attributes['Speed'] = 0
		self.Attributes['Endurance'] = 0
		self.Attributes['Personality'] = 0
		self.Attributes['Luck'] = 0
		#Total of Skills raised in this level
		self.AmountSkillRaised = {}
		self.AmountSkillRaised['Strength'] = 0
		self.AmountSkillRaised['Intelligence'] = 0
		self.AmountSkillRaised['Willpower'] = 0
		self.AmountSkillRaised['Agility'] = 0
		self.AmountSkillRaised['Speed'] = 0
		self.AmountSkillRaised['Endurance'] = 0
		self.AmountSkillRaised['Personality'] = 0
		self.AmountSkillRaised['Luck'] = 0
		#Skills Levels
		self.CurrentSkills = {}
		self.CurrentSkills['Acrobatic'] = 0
		self.CurrentSkills['Armorer'] = 0
		self.CurrentSkills['Axe'] = 0
		self.CurrentSkills['BluntWeapon'] = 0
		self.CurrentSkills['LongBlade'] = 0
		self.CurrentSkills['Alchemy'] = 0
		self.CurrentSkills['Conjuration'] = 0
		self.CurrentSkills['Enchant'] = 0
		self.CurrentSkills['Security'] = 0
		self.CurrentSkills['Alteration'] = 0
		self.CurrentSkills['Destruction'] = 0
		self.CurrentSkills['Mysticism'] = 0
		self.CurrentSkills['Restoration'] = 0
		self.CurrentSkills['Block'] = 0
		self.CurrentSkills['LightArmor'] = 0
		self.CurrentSkills['Marksman'] = 0
		self.CurrentSkills['Sneak'] = 0
		self.CurrentSkills['Athletics'] = 0
		self.CurrentSkills['HandToHand'] = 0
		self.CurrentSkills['ShortBlade'] = 0
		self.CurrentSkills['Unarmored'] = 0
		self.CurrentSkills['HeavyArmor'] = 0
		self.CurrentSkills['MediummArmor'] = 0
		self.CurrentSkills['Spear'] = 0
		self.CurrentSkills['Illusion'] = 0
		self.CurrentSkills['Mercantile'] = 0
		self.CurrentSkills['Speechcraft'] = 0
	def __str__(self):
		old_stdout = sys.stdout  
		result = StringIO()
		sys.stdout = result
		print(f'Strength: {self.AmountSkillRaised["Strength"]}')
		print(f'Intelligence: {self.AmountSkillRaised["Intelligence"]}')
		print(f'Willpower: {self.AmountSkillRaised["Willpower"]}')
		print(f'Agility: {self.AmountSkillRaised["Agility"]}')
		print(f'Speed: {self.AmountSkillRaised["Speed"]}')
		print(f'Endurance: {self.AmountSkillRaised["Endurance"]}')
		print(f'Personality: {self.AmountSkillRaised["Personality"]}')
		print(f'Luck: {self.AmountSkillRaised["Luck"]}',end='')
		sys.stdout = old_stdout
		return result.getvalue()

def GetProcessBaseAddress(process):
	"""
	Given a process, finds it's base address
	"""
	try:
		if "win" in sys.platform:
			modules = (ctypes.wintypes.HMODULE*1)()
			ctypes.windll.psapi.EnumProcessModules(process._WindowsProcess__process_handle, modules, ctypes.sizeof(modules), None)
			return [x for x in tuple(modules) if x != None][0]
		else:
			return 0x0
	except:
		return 0x0

def GetOpenMWWindowProcess(windowTitle="OpenMW"):
	"""
	Gets the process of OpenMW
	"""
	try:
		return PyMemoryEditor.OpenProcess(window_title=windowTitle)
	except:
		return None

def GetCharacterSkillsIncreases(process):
	"""
	Given a PyMemoryEditor process of an OpenMW instance, gets the current total skillups per attributes on the current level
	"""
	baseAddress = GetProcessBaseAddress(process)
	result = OpenMWCharcterLevelUpTotalSkills()
	addressAndOffsets = {}
	addressAndOffsets['Strength'] = [baseAddress+0x015FC3D0,0x30,0x108,0x220,0x118,0x0,0x348,0x0]
	addressAndOffsets['Intelligence'] = [baseAddress+0x015FC3D0,0x30,0x108,0x220,0x118,0x0,0x348,0x4]
	addressAndOffsets['Willpower'] = [baseAddress+0x015FC3D0,0x30,0x108,0x220,0x460,0x8]
	addressAndOffsets['Agility'] = [baseAddress+0x015FC3D0,0x30,0x108,0x220,0x118,0x0,0x348,0xC]
	addressAndOffsets['Speed'] = [baseAddress+0x015FC3D0,0x30,0x108,0x220,0x460,0x10]
	addressAndOffsets['Endurance'] = [baseAddress+0x1603B28,0x330,0x108,0x220,0x460,0x14]
	addressAndOffsets['Personality'] = [baseAddress+0x015FC3D0,0x30,0x108,0x220,0x460,0x18]
	
	for atrib in addressAndOffsets:
		value = 0
		counter = 0
		for address in addressAndOffsets[atrib]:
			counter +=1
			value = process.read_process_memory(value+address,int,8 if counter < len(addressAndOffsets[atrib]) else 4)
		result.AmountSkillRaised[atrib] = value
	return result

#Test
# process = GetOpenMWWindowProcess()
# print(hex(GetProcessBaseAddress(process)))
# for memory_region in process.get_memory_regions():
# 	base_address = memory_region["address"]
# 	print(hex(base_address))
# 	size = memory_region["size"]
# 	information = memory_region["struct"]
# print(GetCharacterSkillsIncreases(process))
# process.close()