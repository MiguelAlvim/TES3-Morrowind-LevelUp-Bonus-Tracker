import ctypes, psutil, enum, sys
import ctypes.wintypes #Added so that PyInstaller works properly
from io import StringIO

#Based on ReadWriteMemory by VSantiago113 (https://github.com/vsantiago113/ReadWriteMemory)
#Curently (11/2024), the lib has no support for 64bit pointers, so I wrote a similar one (albeit, simpler) with the support for 64bit and 32bit addresses + reading varvalues of 4 and 8 bit from RAM

#To collect individual skills levels is a TODO thing... Gotta have some patience to collect the fixed address of all the 26 skills

class MemoryReturnType(enum.Enum):
	"""
	Enum used to represent if the amount of data that we are going to read from RAM is 4 or 8 bytes
	It is necessay for us to read 8 bytes on 64bit addresses, and 4 bytes when reading 32bit integers (the current standard of int size on most languages)
	"""
	BYTE4 = 1
	BYTE8 = 2

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

def GetOpenMWProcessHandle():
	"""
	Seeks the windows processes for an process from an exe named "openmw.exe"
	Do make sure that the user have not changed his openMW .exe name
	"""
	#Kernel32
	kernel32 = ctypes.windll.Kernel32

	#Kernel32 permissions
	PROCESS_QUERY_INFORMATION = 0x0400
	PROCESS_VM_OPERATION = 0x0008
	PROCESS_VM_READ = 0x0010

	dwDesiredAccess = (PROCESS_QUERY_INFORMATION|PROCESS_VM_OPERATION|PROCESS_VM_READ)
	bInheritHandle = False
	dwProcessID = None

	#Finding the OpenMW process
	openMWProcessName="openmw.exe"
	for process in psutil.process_iter(['pid', 'name', 'username']):
		if process.info['name'] == openMWProcessName:
			dwProcessID = process.info['pid']
			break

	if dwProcessID == None:
		return None

	return kernel32.OpenProcess(dwDesiredAccess,bInheritHandle,dwProcessID)

def IsProcessIs64bits(handle):#If false, is 32bits - Thanks to yinkaisheng in https://github.com/giampaolo/psutil/issues/1102
	"""
	A somewhat 'hacky' why to find if a windows program is 32 or 64 bits; If the return is true, it is 64, else is 32
	It is used to properly navigate processes pointers (32 bit processes have 4 byte addresses; 64bit processes ahve 8 byte addresses)
	"""
	#Kernel32
	kernel32 = None
	try:
		kernel32 = ctypes.windll.kernel32
	except Exception as e:
		return False

	is64 = ctypes.c_bool()
	if kernel32.IsWow64Process(handle,ctypes.byref(is64)):
		return False if is64.value else True
	else:		
		return False

def CloseProcessHandle(handle):
	#Kernel32
	kernel32 = ctypes.windll.Kernel32
	kernel32.CloseHandle(handle)

def ReadIntValueInMemory(handle,offsets:list[int]=[],returnByteSize:MemoryReturnType = MemoryReturnType.BYTE4):
	"""
	Given a processes handle, this function will read the contents of the RAM addres as a 32 or 64 integer.

	It uses the base addres of the process to navigate through the declared offsets. If no offset is given, it will read the base addres of the process.

	You must pass even the address of the field you want to read as an offset
	"""
	try:
		baseValue = GetProcessBaseAddress(handle)
		is64 = IsProcessIs64bits(handle)
		counter = len(offsets)
		for offset in offsets:
			counter-=1
			if counter != 0:
				if is64:
					baseValue = ReadProcessMemory(handle,baseValue+offset,MemoryReturnType.BYTE8)
				else:
					baseValue = ReadProcessMemory(handle,baseValue+offset,MemoryReturnType.BYTE4)
			else:
				baseValue = ReadProcessMemory(handle,baseValue+offset,returnByteSize)
		return baseValue
	except:
		return 0

def ReadProcessMemory(handle,lpBaseAddress,returnSize:MemoryReturnType = MemoryReturnType.BYTE4):
	"""
	Reads the content of the address passed in params. It is used on the ReadIntValueInMemory function. Use that one instead
	"""
	#Kernel32
	kernel32 = ctypes.windll.Kernel32
	try:
		if(returnSize == MemoryReturnType.BYTE4):
			readBuffer = ctypes.c_uint32()
		else:
			readBuffer = ctypes.c_uint64()
		lpBuffer = ctypes.byref(readBuffer)
		nSize = ctypes.sizeof(readBuffer)
		lpNumberOfBytesRead = ctypes.c_ulong(0)

		kernel32.ReadProcessMemory(handle,ctypes.c_void_p(lpBaseAddress),lpBuffer,nSize,lpNumberOfBytesRead)
		return readBuffer.value

	except Exception as e:
		print(f"Problem on reading ProcessRAM {kernel32.GetLastError()}")
		return None

def GetProcessBaseAddress(handle):
	"""
	Given a process, finds it's base address
	"""
	try:
		modules = (ctypes.wintypes.HMODULE*1)()
		ctypes.windll.psapi.EnumProcessModules(handle, modules, ctypes.sizeof(modules), None)
		return [x for x in tuple(modules) if x != None][0]
	except:
		return None

def GetOpenMWCurrentLeveUpBonuses(handle) -> OpenMWCharcterLevelUpTotalSkills:
	"""
	Given an OpenMW process handle, reads the current amount of skill of each attribute that the currently loaded character has.
	"""
	result = OpenMWCharcterLevelUpTotalSkills()
	result.AmountSkillRaised['Strength'] = ReadIntValueInMemory(handle,[0x015FC3D0,0x30,0x108,0x220,0x118,0x0,0x348,0x0],MemoryReturnType.BYTE4)
	result.AmountSkillRaised['Intelligence'] = ReadIntValueInMemory(handle,[0x015FC3D0,0x30,0x108,0x220,0x118,0x0,0x348,0x4],MemoryReturnType.BYTE4)
	result.AmountSkillRaised['Willpower'] = ReadIntValueInMemory(handle,[0x015FC3D0,0x30,0x108,0x220,0x460,0x8],MemoryReturnType.BYTE4)
	result.AmountSkillRaised['Agility'] = ReadIntValueInMemory(handle,[0x015FC3D0,0x30,0x108,0x220,0x118,0x0,0x348,0xC],MemoryReturnType.BYTE4)
	result.AmountSkillRaised['Speed'] = ReadIntValueInMemory(handle,[0x015FC3D0,0x30,0x108,0x220,0x460,0x10],MemoryReturnType.BYTE4)
	result.AmountSkillRaised['Endurance'] = ReadIntValueInMemory(handle,[0x015FC3D0,0x30,0x108,0x220,0x460,0x14],MemoryReturnType.BYTE4)
	result.AmountSkillRaised['Personality'] = ReadIntValueInMemory(handle,[0x015FC3D0,0x30,0x108,0x220,0x460,0x18],MemoryReturnType.BYTE4)
	result.AmountSkillRaised['Luck'] = 0
	return result

#Test
#openMWHandle = GetOpenMWProcessHandle()
#print(GetOpenMWCurrentLeveUpBonuses(openMWHandle))

#CloseProcessHandle(openMWHandle)