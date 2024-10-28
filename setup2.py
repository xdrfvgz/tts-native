#!/usr/bin/env python3
import os
import shutil
import argparse
from pathlib import Path
import subprocess
from typing import Optional

class AndroidProjectManager:
    def __init__(self, project_name: str = "TtsApp", package_name: str = "com.example.ttsapp"):
        self.project_name = project_name
        self.package_name = package_name
        self.package_path = package_name.replace(".", "/")
        self.root_dir = Path.cwd()

    def setup_project(self, model_path: Optional[str] = None):
        """Hauptmethode zum Einrichten oder Aktualisieren des Projekts"""
        print("🚀 Starte Projekt-Setup/Update...")
        
        # Erstelle/Update Projektstruktur
        self._ensure_directories()
        self._write_gradle_files()
        self._write_manifest()
        self._write_main_activity()
        self._write_layout()
        
        # Modell-Handling
        if model_path:
            self.copy_model(model_path)
        
        # Gradle Wrapper erstellen falls nicht vorhanden
        self._ensure_gradle_wrapper()
        
        print("✅ Setup/Update abgeschlossen!")
        self._print_next_steps(model_path is None)

    def _ensure_directories(self):
        """Erstellt benötigte Verzeichnisse"""
        dirs = [
            f"app/src/main/java/{self.package_path}",
            "app/src/main/res/layout",
            "app/src/main/res/values",
            "app/src/main/assets/models",
            "gradle/wrapper"
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def copy_model(self, model_path: str):
        """Kopiert ONNX Modell in assets"""
        if not os.path.exists(model_path):
            print(f"⚠️  Modell nicht gefunden: {model_path}")
            return False
            
        target_path = "app/src/main/assets/models/tts_model.onnx"
        shutil.copy2(model_path, target_path)
        print(f"✅ Modell kopiert nach {target_path}")
        return True

    def _write_gradle_files(self):
        """Schreibt alle Gradle-Konfigurationsdateien"""
        # gradle.properties
        with open("gradle.properties", "w") as f:
            f.write("""org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
android.nonTransitiveRClass=true""")

        # settings.gradle
        with open("settings.gradle", "w") as f:
            f.write(f"""include ':app'
rootProject.name = "{self.project_name}"
""")

        # build.gradle (Project)
        with open("build.gradle", "w") as f:
            f.write("""buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.4.2'
        classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:1.8.22'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}""")

        # build.gradle (App)
        with open("app/build.gradle", "w") as f:
            f.write(f"""plugins {{
    id 'com.android.application'
    id 'kotlin-android'
}}

android {{
    namespace '{self.package_name}'
    compileSdk 33

    defaultConfig {{
        applicationId "{self.package_name}"
        minSdk 21
        targetSdk 33
        versionCode 1
        versionName "1.0"

        ndk {{
            abiFilters 'armeabi-v7a', 'arm64-v8a'
        }}
    }}

    buildTypes {{
        release {{
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}

    buildFeatures {{
        viewBinding true
    }}

    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}

    kotlinOptions {{
        jvmTarget = '1.8'
    }}
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.10.1'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'com.microsoft.onnxruntime:onnxruntime-android:1.15.1'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1'
}}""")

    def _write_manifest(self):
        """Schreibt Android Manifest"""
        with open("app/src/main/AndroidManifest.xml", "w") as f:
            f.write(f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.MaterialComponents.DayNight.DarkActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>""")

    def _ensure_gradle_wrapper(self):
        """Stellt sicher dass Gradle Wrapper existiert"""
        if not os.path.exists("gradlew"):
            try:
                subprocess.run(["gradle", "wrapper"], check=True)
                print("✅ Gradle Wrapper erstellt")
            except Exception as e:
                print(f"⚠️  Konnte Gradle Wrapper nicht erstellen: {e}")

    def _print_next_steps(self, needs_model: bool):
        """Zeigt nächste Schritte an"""
        print("\n📝 Nächste Schritte:")
        if needs_model:
            print("1. Führen Sie das Script erneut mit --model PFAD/ZU/MODELL.onnx aus")
        print("2. Führen Sie ./gradlew build aus")
        print("3. Öffnen Sie das Projekt in Android Studio oder bauen Sie mit ./gradlew assembleDebug")

def main():
    parser = argparse.ArgumentParser(description='Android Projekt Setup/Update Tool')
    parser.add_argument('--name', default='TtsApp', help='Projektname')
    parser.add_argument('--package', default='com.example.ttsapp', help='Package Name')
    parser.add_argument('--model', help='Pfad zum ONNX Modell')
    
    args = parser.parse_args()
    
    manager = AndroidProjectManager(args.name, args.package)
    manager.setup_project(args.model)

if __name__ == "__main__":
    main()
