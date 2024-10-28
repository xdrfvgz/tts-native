#!/usr/bin/env python3

def update_gradle():
    """Updated die app/build.gradle um assets auszuschließen"""
    
    with open("app/build.gradle", "r") as f:
        content = f.read()
    
    # Füge android.sourceSets Block hinzu um assets auszuschließen
    if "android {" in content:
        content = content.replace(
            "android {",
            """android {
    sourceSets {
        main {
            assets.srcDirs = [] // Keine Assets kompilieren
        }
    }""")
    
    with open("app/build.gradle", "w") as f:
        f.write(content)
    
    print("✅ Assets ausgeschlossen")

if __name__ == "__main__":
    update_gradle()
