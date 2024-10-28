#!/usr/bin/env python3

def update_gradle():
    """Updated die app/build.gradle um das ONNX Modell einzuschließen"""
    
    with open("app/build.gradle", "r") as f:
        content = f.read()
    
    # Füge android.sourceSets Block hinzu/modifiziere ihn
    if "sourceSets {" not in content:
        content = content.replace(
            "android {",
            """android {
    sourceSets {
        main {
            assets.srcDirs = ['src/main/assets']
        }
    }""")
    
    with open("app/build.gradle", "w") as f:
        f.write(content)

    print("✅ Gradle für Asset-Inclusion aktualisiert")
    print("ℹ️  Kopiere jetzt dein Modell nach app/src/main/assets/models/tts_model.onnx")

if __name__ == "__main__":
    update_gradle()
