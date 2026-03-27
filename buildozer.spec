[app]
title = Currency Converter Pro
package.name = currencyconverterpro
package.domain = org.abdoudesigner

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,mp3,ttf

version = 1.0

requirements = python3,kivy==2.3.0,requests,kivmob

# ملفات الصور و الصوت المطلوبة
source.include_patterns = *.png,*.jpg,*.mp3,*.json

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 34
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.ndk_api = 21

# ✅ مهم لـ KivMob و AdMob
android.gradle_dependencies = com.google.android.gms:play-services-ads:22.6.0
android.enable_androidx = True
android.add_aars = kivmob-0.2.aar

android.archs = arm64-v8a, armeabi-v7a

log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
