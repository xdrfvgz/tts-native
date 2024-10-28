#!/usr/bin/env python3

def update_dependencies():
    """Updated die Dependencies in app/build.gradle"""
    
    with open("app/build.gradle", "r") as f:
        content = f.read()
    
    # Suche die dependencies-Section und füge die neue Dependency hinzu
    if "dependencies {" in content:
        content = content.replace(
            "dependencies {",
            """dependencies {
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.1'"""
        )
    
    with open("app/build.gradle", "w") as f:
        f.write(content)
    
    print("✅ Lifecycle Dependency hinzugefügt")

if __name__ == "__main__":
    update_dependencies()
