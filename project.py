#!/usr/bin/env python3
"""
Android App Workflow Manager - Erstellt und konfiguriert eine Android App mit ONNX Support

Verwendung:
1. Script ausführen zum Erstellen der Basis-App: ./workflow.py init
2. ONNX Modell hinzufügen: ./workflow.py add-model path/to/model.onnx
3. UI anpassen: ./workflow.py customize-ui
4. Build starten: ./workflow.py build
"""

import os
import shutil
from pathlib import Path
import subprocess
import argparse

class AndroidAppManager:
    def __init__(self):
        self.project_name = "TtsApp"
        self.package_name = "com.example.ttsapp"
        self.package_path = "com/example/ttsapp"
        
    def init_project(self):
        """Initialisiert die Basis-Projektstruktur"""
        # Verzeichnisse erstellen
        dirs = [
            f"app/src/main/java/{self.package_path}",
            "app/src/main/res/layout",
            "app/src/main/res/values",
            "app/src/main/res/drawable",
            "app/src/main/assets/models",
            "gradle/wrapper"
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
        # Gradle Konfiguration
        self._write_project_gradle()
        self._write_app_gradle()
        self._write_settings_gradle()
        self._write_gradle_properties()
        
        # Android Manifest
        self._write_manifest()
        
        # Basis Activity & Layout
        self._write_main_activity()
        self._write_activity_layout()
        
        print("✅ Basis-Projekt erstellt")

    def _write_project_gradle(self):
        """Project-level build.gradle"""
        content = """buildscript {
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
}"""
        with open("build.gradle", "w") as f:
            f.write(content)

    def _write_app_gradle(self):
        """App-level build.gradle"""
        content = f"""plugins {{
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

    sourceSets {{
        main {{
            assets.srcDirs = ['src/main/assets']
        }}
    }}
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.10.1'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'com.microsoft.onnxruntime:onnxruntime-android:1.15.1'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.1'
}}"""
        with open("app/build.gradle", "w") as f:
            f.write(content)

    def _write_settings_gradle(self):
        """settings.gradle"""
        content = f"""include ':app'
rootProject.name = "{self.project_name}"
"""
        with open("settings.gradle", "w") as f:
            f.write(content)

    def _write_gradle_properties(self):
        """gradle.properties"""
        content = """android.useAndroidX=true
android.enableJetifier=true"""
        with open("gradle.properties", "w") as f:
            f.write(content)

    def _write_manifest(self):
        """AndroidManifest.xml"""
        content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    
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
</manifest>"""
        with open("app/src/main/AndroidManifest.xml", "w") as f:
            f.write(content)

    def _write_main_activity(self):
        """MainActivity.kt mit ONNX Integration"""
        content = """package com.example.ttsapp

import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.ttsapp.databinding.ActivityMainBinding
import ai.onnxruntime.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private var ortSession: OrtSession? = null
    private var isProcessing = false

    private val getContent = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { loadExternalModel(it) }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupListeners()
        tryLoadingBuiltinModel()
    }

    private fun tryLoadingBuiltinModel() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val modelBytes = assets.open("models/tts_model.onnx").use { it.readBytes() }
                loadModelFromBytes(modelBytes)
                
                withContext(Dispatchers.Main) {
                    binding.modelStatus.text = "Eingebautes Modell aktiv"
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    binding.modelStatus.text = "Kein eingebautes Modell"
                }
            }
        }
    }

    private fun loadExternalModel(uri: Uri) {
        lifecycleScope.launch {
            withContext(Dispatchers.Main) {
                binding.synthesizeButton.isEnabled = false
                binding.loadModelButton.isEnabled = false
                binding.progressBar.visibility = android.view.View.VISIBLE
            }

            try {
                withContext(Dispatchers.IO) {
                    val modelBytes = contentResolver.openInputStream(uri)?.use { it.readBytes() }
                        ?: throw Exception("Konnte Modelldatei nicht lesen")
                    loadModelFromBytes(modelBytes)
                }
                
                withContext(Dispatchers.Main) {
                    binding.modelStatus.text = "Externes Modell aktiv"
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, 
                        "Modelladung fehlgeschlagen: ${e.message}", 
                        Toast.LENGTH_LONG
                    ).show()
                }
            } finally {
                withContext(Dispatchers.Main) {
                    binding.loadModelButton.isEnabled = true
                    binding.progressBar.visibility = android.view.View.GONE
                }
            }
        }
    }

    private suspend fun loadModelFromBytes(modelBytes: ByteArray) {
        val env = OrtEnvironment.getEnvironment()
        ortSession = env.createSession(modelBytes)
        
        withContext(Dispatchers.Main) {
            binding.synthesizeButton.isEnabled = true
            Toast.makeText(this@MainActivity, "Model erfolgreich geladen", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun setupListeners() {
        binding.synthesizeButton.isEnabled = false
        
        binding.loadModelButton.setOnClickListener {
            getContent.launch("application/octet-stream")
        }
        
        binding.synthesizeButton.setOnClickListener {
            if (!isProcessing) {
                val text = binding.inputText.text?.toString() ?: ""
                if (text.isNotEmpty()) {
                    synthesizeText(text)
                } else {
                    Toast.makeText(this, "Bitte Text eingeben", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun synthesizeText(text: String) {
        isProcessing = true
        binding.progressBar.visibility = android.view.View.VISIBLE
        binding.synthesizeButton.isEnabled = false

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val session = ortSession ?: throw Exception("Model nicht geladen")
                
                val inputArray = arrayOf(text)
                val env = OrtEnvironment.getEnvironment()
                val input = OnnxTensor.createTensor(env, inputArray)
                
                val output = session.run(mapOf("text" to input))
                val audioData = output[0].value as Array<*>

                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, 
                        "Audio generiert (${audioData.size} samples)", 
                        Toast.LENGTH_SHORT
                    ).show()
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, 
                        "Fehler: ${e.message}", 
                        Toast.LENGTH_LONG
                    ).show()
                }
            } finally {
                withContext(Dispatchers.Main) {
                    binding.progressBar.visibility = android.view.View.GONE
                    binding.synthesizeButton.isEnabled = true
                    isProcessing = false
                }
            }
        }
    }
}"""
        os.makedirs(f"app/src/main/java/{self.package_path}", exist_ok=True)
        with open(f"app/src/main/java/{self.package_path}/MainActivity.kt", "w") as f:
            f.write(content)

    def _write_activity_layout(self):
        """activity_main.xml"""
        content = """<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="16dp">

    <TextView
        android:id="@+id/modelStatus"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Kein Modell geladen"
        android:textStyle="italic"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />

    <com.google.android.material.textfield.TextInputLayout
        android:id="@+id/textInputLayout"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:hint="Text für Synthese"
        app:layout_constraintTop_toBottomOf="@id/modelStatus">

        <com.google.android.material.textfield.TextInputEditText
            android:id="@+id/inputText"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:inputType="textMultiLine"
            android:lines="3" />

    </com.google.android.material.textfield.TextInputLayout>

    <com.google.android.material.button.MaterialButton
        android:id="@+id/loadModelButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:text="Anderes Modell laden"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/textInputLayout" />

    <com.google.android.material.button.MaterialButton
        android:id="@+id/synthesizeButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="Synthesieren"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/loadModelButton" />

    <ProgressBar
        android:id="@+id/progressBar"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:visibility="gone"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>"""
        with open("app/src/main/res/layout/activity_main.xml", "w") as f:
            f.write(content)

    def add_model(self, model_path):
        """Fügt ein ONNX Modell zum Projekt hinzu"""
        if not os.path.exists(model_path):
            print("❌ Modell-Datei nicht gefunden")
            return

        target_dir = "app/src/main/assets/models"
        target_path = f"{target_dir}/tts_model.onnx"
        
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(model_path, target_path)
        print(f"✅ Modell kopiert nach {target_path}")

    def customize_ui(self):
        """UI-Anpassungen vornehmen"""
        # strings.xml
        strings_content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">TTS App</string>
</resources>"""
        os.makedirs("app/src/main/res/values", exist_ok=True)
        with open("app/src/main/res/values/strings.xml", "w") as f:
            f.write(strings_content)
            
        # Platzhalter-Icons erstellen
        for dpi in ['mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']:
            path = f"app/src/main/res/mipmap-{dpi}"
            os.makedirs(path, exist_ok=True)
            
            for icon_name in ['ic_launcher', 'ic_launcher_round']:
                with open(f"{path}/{icon_name}.png", "wb") as f:
                    # 1x1 transparentes PNG
                    f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\xd7c\x60\x60\x00\x00\x00\x02\x00\x01\xe5\x27\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82')
        
        print("✅ UI-Ressourcen aktualisiert")

    def build(self):
        """Build-Prozess starten"""
        # Gradle Wrapper erstellen falls nicht vorhanden
        if not os.path.exists("gradlew"):
            try:
                subprocess.run(["gradle", "wrapper"], check=True)
                print("✅ Gradle Wrapper erstellt")
            except Exception as e:
                print(f"⚠️  Konnte Gradle Wrapper nicht erstellen: {e}")
                return

        # Debug APK bauen
        try:
            subprocess.run(["./gradlew", "assembleDebug"], check=True)
            apk_path = "app/build/outputs/apk/debug/app-debug.apk"
            if os.path.exists(apk_path):
                print(f"✅ APK erfolgreich erstellt: {apk_path}")
            else:
                print("❌ APK konnte nicht gefunden werden")
        except subprocess.CalledProcessError as e:
            print(f"❌ Build fehlgeschlagen: {e}")

def main():
    parser = argparse.ArgumentParser(description="Android App Workflow Manager")
    subparsers = parser.add_subparsers(dest='command', help='Verfügbare Befehle')

    # init Command
    init_parser = subparsers.add_parser('init', help='Erstellt neue Android App')
    
    # add-model Command
    model_parser = subparsers.add_parser('add-model', help='Fügt ONNX Modell hinzu')
    model_parser.add_argument('model_path', help='Pfad zum ONNX Modell')
    
    # customize-ui Command
    ui_parser = subparsers.add_parser('customize-ui', help='UI anpassen')
    
    # build Command
    build_parser = subparsers.add_parser('build', help='APK erstellen')

    args = parser.parse_args()
    manager = AndroidAppManager()

    if args.command == 'init':
        manager.init_project()
    elif args.command == 'add-model':
        manager.add_model(args.model_path)
    elif args.command == 'customize-ui':
        manager.customize_ui()
    elif args.command == 'build':
        manager.build()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
