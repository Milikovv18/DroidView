# DroidView Desktop Component  

This repository contains the desktop component of the DroidView project. The following instructions will guide you through setting up and running this module.  

## Manual Installation  

### Step 1: Initialize Environment  
The desktop side of the project consists mainly of Python code. To set it up, follow these steps:  

1. **Create a virtual environment** using `venv`:  
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:  
   - On Windows:  
     ```
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:  
     ```
     source ./venv/bin/activate
     ```

3. **Install dependencies** from `requirements.txt`:  
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure that the file `../android/app/build/outputs/apk/debug/app-debug.apk` exists. If not, refer to the instructions in the `../android` folder for compiling it.  

### Step 2: Run the Application  
After completing the setup, you can run the application using:  
```bash
python main.py
```

## Description  

The desktop component of DroidView uses **PyQt6** for drawing the user interface and **PyOpenGL** to render the main 3D scene. It runs an RTMP server to receive real-time Android screen state data. Additionally, a separate HTTP server is planned for handling non-real-time requests.  

## License  

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
