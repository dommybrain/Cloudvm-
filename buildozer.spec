[app]
title = FoxyScanner
package.name = foxyscanner
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,certifi,urllib3,charset-normalizer,idna,openssl,pyopenssl
orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1

[buildozer]
log_level = 2

[android]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.permissions = INTERNET
android.archs = arm64-v8a
