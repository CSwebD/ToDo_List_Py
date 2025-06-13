# Advanced ToDo List App (Tkinter Desktop App)

A feature-rich Python desktop application to manage your daily tasks efficiently. Built with Tkinter, this app lets you track, complete, and analyze your productivity using real-time charts.

---

## Features

- 🆔 Unique Task IDs (A–Z)
- ✅ Mark tasks as Done or Skipped
- 🔄 Undo / Redo support
- 📊 Daily, Weekly, Monthly Stats
- 📈 7-Day Task Completion Chart
- 📉 Per-Task Performance Chart
- 💾 Persistent data storage (`todo_data.json`)

---

## Screenshot

<img src="screenshot.png" alt="Screenshot of App" width="600">

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/CSwebD/todo-app.git
cd todo-app

### 2. Install Required Packages

```bash
pip install -r requiements.txt

### 3. Run the program

```bash
python todo.py

### 4. How to run this application as .exe (Window)?

#### Step 1: Install PyInstaller

```bash
pip install pyinstaller

#### Step 2: Create Executable

```bash
python -m PyInstaller --onefile --windowed todo.py

#### Step 3: Change the design of icon (Optional)

- Go to eg. icon8.com and find relevant icon, download it;
- Go to eg. icoconverter and convert this (eg png) to ICO, and save for eg as (Image.ico);
- Right click on .exe file and press `Send to` and next `Desktop (create shortcut)`;
- Go to Desktop, find that Shortcut, press right click and choose Properties;
- Next choose Shortcut, and next `Change icon...`
- Browse where the Image.ico (this should be on the same folder), choose it and next ok, apply, ok and close.



