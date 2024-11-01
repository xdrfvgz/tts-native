#!/usr/bin/env python3

def create_hybrid_loader():
    """Erstellt MainActivity mit zwei Lademöglichkeiten"""
    
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
                // Versuche das eingebaute Modell zu laden
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
        binding.synthesizeButton.isEnabled = false
        binding.loadModelButton.isEnabled = false
        binding.progressBar.visibility = android.view.View.VISIBLE

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val modelBytes = contentResolver.openInputStream(uri)?.use { it.readBytes() }
                    ?: throw Exception("Konnte Modelldatei nicht lesen")

                loadModelFromBytes(modelBytes)
                
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
                        Toast_LENGTH_SHORT
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

    # Write files
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "w") as f:
        f.write(content)
    
    with open("app/src/main/res/layout/activity_main.xml", "w") as f:
        f.write(layout)
    
    print("✅ Hybrid Model Loading implementiert")

if __name__ == "__main__":
    create_hybrid_loader()
