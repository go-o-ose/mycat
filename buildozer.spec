[app]
title = Мой Кот
package.name = mycat
package.domain = org.mycat

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = assets/*,images/*

version = 0.1

requirements = python3,kivy==2.2.1

orientation = portrait
fullscreen = 1

icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

android.archs = arm64-v8a
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.allow_backup = True

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 0
