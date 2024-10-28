#!/usr/bin/env python3
import os
import zipfile

def check_apk():
    """Überprüft den Inhalt der APK"""
    apk_path = "app/build/outputs/apk/debug/app-debug.apk"
    
    with zipfile.ZipFile(apk_path) as apk:
        files = apk.namelist()
        onnx_files = [f for f in files if f.endswith('.onnx')]
        
        print("Gefundene ONNX Dateien:")
        for f in onnx_files:
            info = apk.getinfo(f)
            original = info.file_size
            compressed = info.compress_size
            print(f"{f}: {original/1024/1024:.1f}MB (komprimiert: {compressed/1024/1024:.1f}MB)")

if __name__ == "__main__":
    check_apk()
