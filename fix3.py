#!/usr/bin/env python3

def create_file_chooser():
    content = """package com.example.ttsapp

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
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
        uri?.let { loadModel(it) }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupListeners()
        checkPermission()
    }

    private fun checkPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE),
                1)
        }
    }

    private fun loadModel(uri: Uri) {
        binding.synthesizeButton.isEnabled = false
        binding.loadModelButton.isEnabled = false
        binding.progressBar.visibility = android.view.View.VISIBLE

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val modelBytes = contentResolver.openInputStream(uri)?.use { it.readBytes() }
                    ?: throw Exception("Konnte Modelldatei nicht lesen")

                val env = OrtEnvironment.getEnvironment()
                ortSession = env.createSession(modelBytes)

                withContext(Dispatchers.Main) {
                    binding.synthesizeButton.isEnabled = true
                    binding.loadModelButton.isEnabled = true
                    binding.progressBar.visibility = android.view.View.GONE
                    Toast.makeText(this@MainActivity, "Model erfolgreich geladen", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    binding.loadModelButton.isEnabled = true
                    binding.progressBar.visibility = android.view.View.GONE
                    Toast.makeText(this@MainActivity, 
                        "Modelladung fehlgeschlagen: ${e.message}", 
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
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

    # Layout Update
    layout = """<?xml version="1.0" encoding="utf-8"?>
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
        android:id="@+id/loadModelButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:text="Modell laden"
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

    # Update AndroidManifest to include storage permission
    manifest = """<?xml version="1.0" encoding="utf-8"?>
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

    # Write files
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "w") as f:
        f.write(content)
    
    with open("app/src/main/res/layout/activity_main.xml", "w") as f:
        f.write(layout)
        
    with open("app/src/main/AndroidManifest.xml", "w") as f:
        f.write(manifest)
    
    print("✅ File Chooser Implementation hinzugefügt")

if __name__ == "__main__":
    create_file_chooser()
