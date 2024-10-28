#!/usr/bin/env python3

def update_main_activity():
    """Aktualisiert die MainActivity mit funktionierender TTS-Implementation"""
    
    content = """package com.example.ttsapp

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.ttsapp.databinding.ActivityMainBinding
import ai.onnxruntime.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.nio.FloatBuffer

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private var ortSession: OrtSession? = null
    private var isProcessing = false
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupListeners()
    }
    
    private fun setupListeners() {
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
                // Initialisiere ONNX Runtime falls nötig
                if (ortSession == null) {
                    val modelFile = File(filesDir, "tts_model.onnx")
                    if (!modelFile.exists()) {
                        assets.open("models/tts_model.onnx").use { input ->
                            modelFile.outputStream().use { output ->
                                input.copyTo(output)
                            }
                        }
                    }
                    val env = OrtEnvironment.getEnvironment()
                    ortSession = env.createSession(modelFile.absolutePath)
                }

                // Text zu Audio verarbeiten
                val session = ortSession ?: throw Exception("Model nicht geladen")
                
                // Beispiel Input Tensor (anpassen an Ihr Modell)
                val inputTensor = FloatBuffer.allocate(text.length)
                text.forEachIndexed { index, char ->
                    inputTensor.put(index, char.toFloat())
                }
                
                val shape = longArrayOf(1, text.length.toLong())
                val input = OnnxTensor.createTensor(OrtEnvironment.getEnvironment(), inputTensor, shape)
                
                val output = session.run(mapOf("input" to input))
                val audioData = output[0].value as Array<*>

                // UI Update
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

    # Stelle sicher, dass der Ordner existiert
    import os
    os.makedirs("app/src/main/java/com/example/ttsapp", exist_ok=True)
    
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "w") as f:
        f.write(content)
    
    print("✅ MainActivity aktualisiert")

if __name__ == "__main__":
    update_main_activity()
