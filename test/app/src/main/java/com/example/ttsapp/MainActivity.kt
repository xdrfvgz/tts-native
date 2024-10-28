package com.example.ttsapp

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
}