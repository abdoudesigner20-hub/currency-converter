[app]

# اسم التطبيق
title = Currency Converter Pro

# اسم الحزمة
package.name = currencyconverter

# نطاق الحزمة
package.domain = org.abdou

# مجلد الكود
source.dir = .

# الملفات المضمنة — أضفنا mp3 و json
source.include_exts = py,png,jpg,kv,atlas,mp3,json

# إصدار التطبيق
version = 1.0

# المكتبات المطلوبة — هذا هو الأهم!
requirements = python3,kivy,kivmob,requests,android

# الاتجاه
orientation = portrait

# ملء الشاشة
fullscreen = 0

# الصلاحيات — الإنترنت ضروري لجلب أسعار العملات
android.permissions = INTERNET

# API المستهدف
android.api = 33

# الحد الأدنى
android.minapi = 21

# إصدار NDK
android.ndk = 25b

# قبول الرخصة تلقائياً
android.accept_sdk_license = True

# المعمارية (arm64 للهواتف الحديثة + armeabi للقديمة)
android.archs = arm64-v8a, armeabi-v7a

# النسخ الاحتياطي
android.allow_backup = True

#
# OSX (اتركها كما هي)
#
osx.python_version = 3
osx.kivy_version = 1.9.1

#
# iOS (اتركها كما هي)
#
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 1
