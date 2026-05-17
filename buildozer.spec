[app]
title = Foxy Scanner Pro
package.name = foxyscanner
package.domain = org.foxy

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 4.2

# IMPORTANT: لا تثبت python version هنا
requirements = python3, kivy, kivymd, requests, certifi, urllib3, charset-normalizer, idna, pyopenssl

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE, WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# مهم جدًا للاستقرار
android.archs = arm64-v8a, armeabi-v7a

# إصلاح مشاكل SSL / build
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
