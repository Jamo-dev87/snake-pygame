# Snake (Pygame)

A clean, step-by-step implementation of the classic Snake game using Python and Pygame.  
Built as a learning project to demonstrate Python fundamentals, game loops, event handling, and clean coding practices.

---

## 🎮 Features
- Grid-based movement with fixed time steps
- Arrow keys / WASD control
- Customisable game speed
- Clear, modular code structure
- Simple, responsive graphics using Pygame

---

## 🚀 How to Run
**macOS** — using Terminal
Open Terminal (how to find it)

Press ⌘ + Space to open Spotlight, type Terminal, press Return.
or

Finder → Applications → Utilities → Terminal.

Go to your project folder

In Terminal, type cd (with a space), then drag your project folder from Finder into the Terminal window → press Return.
(You should now be “in” your project. Run ls — you should see src, README.md, etc.)

**Windows** — using Terminal / PowerShell / Git Bash
Open a terminal (how to find it)

Press the Windows key, type Terminal (or PowerShell), press Enter.
or

If you installed Git for Windows, open Git Bash (Start menu).
pro tip: In File Explorer, go to your project folder, click the address bar, type cmd and press Enter to open a Command Prompt in that folder.

1. **Clone the repository**
   ```bash
   git clone git@github.com:Jamo-dev87/snake-pygame.git
   cd snake-pygame
## (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

## Install dependencies
pip install -r requirements.txt

## Run the game
python -m src.main

## 🎯 Controls
Arrow keys or WASD → Move

Esc → Quit

## 🛠 Tech Stack
Python 3.12

Pygame 2.5+
