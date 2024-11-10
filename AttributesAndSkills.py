attributesAndSkills = []
"""Complete list with all attributes and related skills of TES 3:Morrowind
"""

class skill:
	"""Represents an skill of TES 3: Morrowind
	"""
	def __init__(self,name:str):
		"""
		:param name Skill Name
		"""
		self.name:str = name
	def __str__(self):
		return self.name

class attribute:
	"""Represents an attribute of TES 3: Morrowind
	"""
	def __init__(self,name:str,abrev:str):
		"""
		:param name Atribute Name
		:param abrev Atribute Abreviation
		"""
		self.name:str = name
		self.abrev:str = abrev
		self.skills:list[skill] = []
	def __str__(self):
		returnStr = "["+self.name +"]"+ ('','\n')[len(self.skills)>0]
		for skill in self.skills:			
			prefix = '╚'
			sufix = ''
			if skill != self.skills[-1]:
				prefix = '╠'
				sufix = '\n'
			returnStr = returnStr + prefix + skill.__str__() + sufix
		return returnStr

#Strength
Strength = attribute("Strength","STR")
Strength.skills.append(skill("Acrobatic"))
Strength.skills.append(skill("Armorer"))
Strength.skills.append(skill("Axe"))
Strength.skills.append(skill("Blunt Weapon"))
Strength.skills.append(skill("Long Blade"))
attributesAndSkills.append(Strength)
#Intelligence
Intelligence = attribute("Intelligence","INT")
Intelligence.skills.append(skill("Alchemy"))
Intelligence.skills.append(skill("Conjuration"))
Intelligence.skills.append(skill("Enchant"))
Intelligence.skills.append(skill("Security"))
attributesAndSkills.append(Intelligence)
#Willpower
Willpower = attribute("Willpower","WLL")
Willpower.skills.append(skill("Alteration"))
Willpower.skills.append(skill("Destruction"))
Willpower.skills.append(skill("Mysticism"))
Willpower.skills.append(skill("Restoration"))
attributesAndSkills.append(Willpower)
#Agility
Agility = attribute("Agility","AGI")
Agility.skills.append(skill("Block"))
Agility.skills.append(skill("Light Armor"))
Agility.skills.append(skill("Mysticism"))
Agility.skills.append(skill("Restoration"))
attributesAndSkills.append(Agility)
#Speed
Speed = attribute("Speed","SPD")
Speed.skills.append(skill("Athletics"))
Speed.skills.append(skill("Hand to Hand"))
Speed.skills.append(skill("Short Blade"))
Speed.skills.append(skill("Unarmored"))
attributesAndSkills.append(Speed)
#Endurance
Endurance = attribute("Endurance","END")
Endurance.skills.append(skill("Heavy Armor"))
Endurance.skills.append(skill("Mediumm Armor"))
Endurance.skills.append(skill("Spear"))
attributesAndSkills.append(Endurance)
#Personality
Personality = attribute("Personality","PER")
Personality.skills.append(skill("Illusion"))
Personality.skills.append(skill("Mercantile"))
Personality.skills.append(skill("Speechcraft"))
attributesAndSkills.append(Personality)
#Luck
Luck = attribute("Luck","LCK")
attributesAndSkills.append(Luck)

#print(*attributesAndSkills, sep='\n\n')