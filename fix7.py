#!/usr/bin/env python3

def fix_toast():
    """Korrigiert den Toast LENGTH_SHORT Bezeichner"""
    
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "r") as f:
        content = f.read()
    
    # Korrigiere den Tippfehler
    content = content.replace(
        "Toast_LENGTH_SHORT",
        "Toast.LENGTH_SHORT"
    )
    
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "w") as f:
        f.write(content)
    
    print("✅ Toast Konstante korrigiert")

if __name__ == "__main__":
    fix_toast()
