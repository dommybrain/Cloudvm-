[app]
title = Foxy Scanner Pro
package.name = foxyscanner
package.domain = org.foxy

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 4.2
# التعديل الأهم: تحديد إصدارات دقيقة لـ Kivy و KivyMD متوافقة مع الأندرويد، مع إضافة حزم تشفير الاتصالات
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,certifi,urllib3,charset-normalizer,idna,openssl,pyopensslorientation = portrait
osx.kivy_version = 2.2.1
fullscreen = 0

# الصلاحيات الكاملة للاتصال بالإنترنت وقراءة وحفظ ملف التقرير hits.txt
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.private_storage = True

# إعدادات المعمارية لضمان عمل التطبيق على الهواتف الحديثة (64-bit) والقديمة
android.arch32 = False
android.arch64 = True

# السماح للـ الكود بطلب الصلاحيات برمجياً أثناء التشغيل
android.grant_caches = True

[buildozer]
log_level = 2
warn_on_root = 1
