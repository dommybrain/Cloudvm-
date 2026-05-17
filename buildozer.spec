[app]
title = Foxy Scanner Pro
package.name = foxyscanner
package.domain = org.foxy

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 4.2

requirements = python3, kivy, kivymd, requests, certifi, urllib3, charset-normalizer, idna, pyopenssl

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

android.archs = arm64-v8a, armeabi-v7a

# 🔥 Release build (important)
android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
