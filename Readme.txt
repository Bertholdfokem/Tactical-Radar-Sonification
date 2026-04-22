========================================================================
PROJECT: HCASA Mission 1 - QuadraControl Symphony (Tactical Radar Edition)
AUTHORS: Bertold & Loic
DATE: January 2026
MODULE: W 1270 - Human Control of Automated Systems in Aviation
========================================================================

--- 1. PROJECT DESCRIPTION ---
This software is an interactive sonification interface designed as a 
Tactical Air Traffic Control Radar. It spatializes four distinct sound 
sources placed at the four corners of the screen. The user controls an 
aircraft, and the audio mix changes dynamically based on the aircraft's 
proximity to each corner.

Key Innovative Features:
- "Military Radar" style GUI with CRT effect (Scanlines).
- Smart Flight Tag that dynamically orients towards the center.
- Real-time Signal Analysis HUD (Heads-Up Display).
- Visual Target Lock and Sonic Tension management.
- Physics Simulation: Dynamic smoke trails and realistic drop shadow.

--- 2. SYSTEM REQUIREMENTS ---
- Python 3.x installed.
- Pygame library installed.

To install Pygame, open a terminal/command prompt and type:
   pip install pygame

--- 3. SUBMISSION CONTENT & FILE STRUCTURE ---
The submission folder contains the following files:

[SOURCE CODE & ASSETS]
- index.py           : The main Python application script.
- avion.png          : The tactical aircraft sprite.
- haut_gauche.mp3    : High Pitch / Melody (Top Left Corner).
- haut_droite.mp3    : High Pitch / Melody (Top Right Corner).
- bas_gauche.mp3     : Low Pitch / Bass (Bottom Left Corner).
- bas_droite.mp3     : Low Pitch / Bass (Bottom Right Corner).

[DOCUMENTATION]
- README.txt         : This installation manual.
- Report.pdf         : The project report (Process, Challenges, Reflection).
- Demo_Video.mp4     : A 2-minute video demonstrating the software.

--- 4. HOW TO RUN ---
1. Open a terminal or command prompt.
2. Navigate to the project folder:
   cd path/to/your/folder
3. Run the script:
   python index.py

--- 5. CONTROLS ---
- MOUSE: Move the aircraft within the airspace.
- 'M' KEY: Mute / Unmute sound.
- 'R' KEY: Reset position to center.
- 'ESC' KEY: Quit the application.

========================================================================