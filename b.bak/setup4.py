#!/usr/bin/env python3
import os

def create_icons():
    """Erstellt einfache App-Icons"""
    
    # Verzeichnisse erstellen
    for dpi in ['mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']:
        path = f"app/src/main/res/mipmap-{dpi}"
        os.makedirs(path, exist_ok=True)
        
        # Platzhalter-Icon erstellen
        for icon_name in ['ic_launcher', 'ic_launcher_round']:
            with open(f"{path}/{icon_name}.png", "wb") as f:
                # Ein 1x1 transparentes PNG
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\xd7c\x60\x60\x00\x00\x00\x02\x00\x01\xe5\x27\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82')

    print("✅ Icons erstellt")

if __name__ == "__main__":
    create_icons()
