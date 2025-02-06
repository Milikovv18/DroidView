# DroidView Android Component

This repository contains the Android component of the DroidView project. The following instructions will guide you through setting up and compiling this module.

## Manual Installation

### Step 1: Initialize Submodule
First, ensure that the `rtmp_muxer` repository is downloaded. If not already present, run the following command from the root directory of the current repository:  
```bash
git submodule update --init
```

### Step 2: Apply Patch (if needed)
The included `rtmp_muxer.patch` file addresses some edge cases in the RTMP implementation and updates the gradle version for compatibility. To apply this patch, navigate to the `android` folder and run:  
```bash
patch -p0 < rtmp_muxer.patch
```

### Step 3: Compile Using Android Studio
This project has been tested using Android Studio. Open the `android` folder in Android Studio and compile the APK as usual. The compiled APK (`app-debug.apk`) will be generated in the following directory:  
```
/android/app/build/outputs/apk/debug/
```

## Further Steps
For complete setup instructions, refer to the guidelines provided in the `../desktop` folder.

## Description
The current project structure is subject to change due to upcoming updates related to Android 14-15 policies affecting the MediaRecorder API.  

## License
This project is licensed under the MIT License (excluding RTMP submodule) - see the [LICENSE](../LICENSE) file for details.
