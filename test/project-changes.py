#!/usr/bin/env python3

def create_resources():
    """Erstellt die fehlenden App-Ressourcen"""
    import os

    # strings.xml
    os.makedirs("app/src/main/res/values", exist_ok=True)
    with open("app/src/main/res/values/strings.xml", "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">TTS App</string>
</resources>""")

    # Icons erstellen
    for dpi in ['mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']:
        icon_dir = f"app/src/main/res/mipmap-{dpi}"
        os.makedirs(icon_dir, exist_ok=True)
        
        for icon_name in ['ic_launcher', 'ic_launcher_round']:
            icon_path = f"{icon_dir}/{icon_name}.png"
            with open(icon_path, "wb") as f:
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\xd7c\x60\x60\x00\x00\x00\x02\x00\x01\xe5\x27\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82')
    
    print("✅ App-Ressourcen erstellt")

if __name__ == "__main__":
    create_resources()
