#!/usr/bin/env python3

def quick_fix():
    """Fixe die AndroidX Probleme mit minimalen Änderungen"""
    
    # Erstelle gradle.properties falls nicht vorhanden
    with open("gradle.properties", "w") as f:
        f.write("android.useAndroidX=true\nandroid.enableJetifier=true")
    
    print("✅ Fixes angewendet - führen Sie nun ./gradlew build aus")

if __name__ == "__main__":
    quick_fix()
