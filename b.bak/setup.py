#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import subprocess

def create_project_structure():
    """Erstellt die komplette Projektstruktur für eine Android App"""
    
    # Basis-Projektstruktur
    project_name = "TtsApp"
    base_package = "com.example.ttsapp"
    package_path = base_package.replace(".", "/")
    
    # Hauptverzeichnisse
    dirs = [
        "app/src/main/java/" + package_path,
        "app/src/main/res/layout",
        "app/src/main/res/values",
        "app/src/main/res/drawable",
        "app/src/main/assets/models",
        "gradle/wrapper"
    ]
    
    # Erstelle alle Verzeichnisse
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # build.gradle (Project Level)
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
}

task clean(type: Delete) {
    delete rootProject.buildDir
}""")

    # build.gradle (App Level)
    with open("app/build.gradle", "w") as f:
        f.write("""plugins {
    id 'com.android.application'
    id 'kotlin-android'
}

android {
    namespace 'com.example.ttsapp'
    compileSdk 33

    defaultConfig {
        applicationId "com.example.ttsapp"
        minSdk 21
        targetSdk 33
        versionCode 1
        versionName "1.0"

        ndk {
            abiFilters 'armeabi-v7a', 'arm64-v8a'
        }
    }

    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }

    buildFeatures {
        viewBinding true
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = '1.8'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.10.1'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'com.microsoft.onnxruntime:onnxruntime-android:1.15.1'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1'
}""")

    # settings.gradle
    with open("settings.gradle", "w") as f:
        f.write("""include ':app'
rootProject.name = "TtsApp"
""")

    # local.properties
    android_sdk = os.getenv("ANDROID_HOME", "/path/to/your/android/sdk")
    with open("local.properties", "w") as f:
        f.write(f"sdk.dir={android_sdk}")

    # MainActivity.kt
    with open(f"app/src/main/java/{package_path}/MainActivity.kt", "w") as f:
        f.write("""package com.example.ttsapp

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.ttsapp.databinding.ActivityMainBinding
import ai.onnxruntime.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private var ortSession: OrtSession? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupOnnxRuntime()
        setupUI()
    }
    
    private fun setupOnnxRuntime() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val modelFile = File(filesDir, "tts_model.onnx")
                assets.open("models/tts_model.onnx").use { input ->
                    modelFile.outputStream().use { output ->
                        input.copyTo(output)
                    }
                }
                
                val env = OrtEnvironment.getEnvironment()
                ortSession = env.createSession(modelFile.absolutePath)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    
    private fun setupUI() {
        binding.synthesizeButton.setOnClickListener {
            // Hier kommt Ihre TTS-Logik hin
        }
    }
}""")

    # activity_main.xml
    with open("app/src/main/res/layout/activity_main.xml", "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="16dp">

    <com.google.android.material.textfield.TextInputLayout
        android:id="@+id/textInputLayout"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Text für Synthese"
        app:layout_constraintTop_toTopOf="parent">

        <com.google.android.material.textfield.TextInputEditText
            android:id="@+id/inputText"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:inputType="textMultiLine"
            android:lines="3" />

    </com.google.android.material.textfield.TextInputLayout>

    <com.google.android.material.button.MaterialButton
        android:id="@+id/synthesizeButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:text="Synthesieren"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/textInputLayout" />

    <ProgressBar
        android:id="@+id/progressBar"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:visibility="gone"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>""")

    # AndroidManifest.xml
    with open("app/src/main/AndroidManifest.xml", "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
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

    # strings.xml
    with open("app/src/main/res/values/strings.xml", "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">TTS App</string>
</resources>""")

    # Gradle Wrapper Properties
    with open("gradle/wrapper/gradle-wrapper.properties", "w") as f:
        f.write("""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-7.6.1-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists""")

def main():
    """Hauptfunktion zum Erstellen des Projekts"""
    print("🚀 Erstelle Android-Projekt...")
    create_project_structure()
    print("✅ Projekt-Struktur erstellt!")
    
    print("\n📝 Folgende Schritte sind noch notwendig:")
    print("1. Kopieren Sie Ihr ONNX-Modell nach app/src/main/assets/models/tts_model.onnx")
    print("2. Setzen Sie den korrekten SDK-Pfad in local.properties")
    print("3. Führen Sie ./gradlew build aus, um das Projekt zu kompilieren")
    print("\n🎉 Fertig! Das Projekt ist nun bereit für die Entwicklung!")

if __name__ == "__main__":
    main()
