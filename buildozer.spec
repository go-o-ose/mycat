[app]

# (string) Title of your application
title = Мой Кот

# (string) Package name
package.name = mycat

# (string) Package domain (needed for android packaging)
package.domain = org.mycat

# (string) Source code where the main.py lives
source.dir = .

# (list) Source files to include (добавил json, как у тебя)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,images/*

# (string) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# ЖЕСТКАЯ ФИКСАЦИЯ НА PYTHON 3.10 — это решит проблему с 3.14
requirements = python3==3.10.12, kivy, hostpython3==3.10.12

# (str) Custom source for target database (override default source)
p4a.branch = master

# (str) Supported orientations (one of landscape, portrait or all)
orientation = portrait

# (bool) Use fullscreen mode or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (int) Android API to use (34 — актуальный стандарт)
android.api = 34

# (int) Minimum API required
android.minapi = 26

# (str) The Android arch to build for (собираем под оба типа процессоров: 32 и 64 бит)
android.archs = armeabi-v7a, arm64-v8a

# (bool) Allow service execution
android.allow_backup = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
