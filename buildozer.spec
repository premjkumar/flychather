[app]

# (str) Title of your application
title = Fly Catcher

# (str) Package name
package.name = flycatcher

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,ttf,wav,ogg

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pygame

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = sensorLandscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
# android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) If True, then automatically accept SDK licenses
android.accept_sdk_licenses = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with debug output of commands))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1
