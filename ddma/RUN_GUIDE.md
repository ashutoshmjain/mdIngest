# 🚀 DDMA User & Launch Guide

This guide explains how to start, use, and shut down the **DeepDive Media Automator (DDMA)** application in my absence, even if you have absolutely no background in Python or command lines.

---

## 🎬 How to Start the App (1-Click Method)

To run the application, you do not need to type any code. Follow these simple steps:

1. **Open the Project Folder:** Open the DDMA project folder (`deepDive/ddma`) in Windows File Explorer.
2. **Double-Click the Launcher:** Double-click the file named **`start_curator.bat`** (the file we just created for you).
3. **Keep the Console Open:** A black command prompt window will open showing:
   `Server started on http://localhost:8000`
   *Keep this window open while you work. If you close it, the app will stop.*
4. **Open the Webpage:** Open your browser and go to:
   👉 **[http://localhost:8000/curator.html](http://localhost:8000/curator.html)**

---

## 📁 What is the `venv` Folder? (Virtual Environment)

When the Antigravity IDE suggested creating a **virtual environment (`venv` / `.venv`)**, it was setting up a private sandbox on your computer.

### In Plain Terms:
* **The Problem:** Python programs often require specific libraries (packages) to run. If different programs on your computer use different versions of those libraries, they can conflict and break.
* **The Solution (`venv`):** A virtual environment is a **dedicated folder** containing its own private copy of Python and all the required libraries for this project. 
* **The Benefit:** It ensures the DDMA tool runs reliably without affecting (or being affected by) any other software on your PC. It's like a private toolbox created just for this project.

---

## 💾 How Saving Works

* The web interface automatically sends your edits (duration inputs, titles, crossfades) back to the running local server.
* The server then writes those updates to the project `plan.json` file on your computer (under `deepDive/ddma/projects/<project>/`, synced to the `dd_hub` workspace).
* **CRITICAL:** If the black console window is closed (or the server is stopped), the webpage won't be able to communicate with the disk, and your changes **will not save**. Always make sure the console is running before editing!

---

## 🛑 How to Stop the App

When you are finished working:
1. Go to the black command prompt window.
2. Press **`Ctrl + C`** on your keyboard (or click the **`X`** close button in the top-right corner of the window).
3. The server will shut down safely.
