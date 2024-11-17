# TES3-Morrowind-LevelUp-Bonus-Tracker
![GitHub License](https://img.shields.io/github/license/miguelalvim/TES3-Morrowind-LevelUp-Bonus-Tracker)
![GitHub Release](https://img.shields.io/github/v/release/MiguelAlvim/TES3-Morrowind-LevelUp-Bonus-Tracker)

Software designed to help the tracking of level up bonuses for **The Elder Scrools 3:Morrowind**

As per [the UESP article](https://en.uesp.net/wiki/Morrowind:Level), attributes bonus on level up are controlled by how many skills attache to said attribute the player has increased on the current level. It goes from +1 at 0 skills increased up to +5 at 10 or more skills increased. This software has a standalone GUI that helps a player to keep track of those skill increases in order to allow him to better optimize his level ups, if he so desires.

This program also allows for users playing on [OpenMW](https://github.com/OpenMW/openmw), to read their level up bonuses in real time while playing. The program will automatically read their current level up bonuses and keep track for them during gameplay.

Written in Python 3.10 with [FreeSimpleGUI 5.1.0](https://github.com/spyoungtech/FreeSimpleGUI) as a dependency for the GUI and [PyMemoryEditor](https://github.com/JeanExtreme002/PyMemoryEditor) for process memory access (from version 1.1.0 forward; 1.0.X access Windows Kernel32 directly).

Icon source: https://www.steamgriddb.com/icon/6187

Execute main.pyw with Python 3.10.X or newer or download a release to run it as a standalone application
