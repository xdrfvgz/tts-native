package com.example.ttsapp

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import com.example.ttsapp.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    private var _binding: ActivityMainBinding? = null
    private val binding get() = _binding!!

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        _binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Minimale UI Initialisierung
        binding.synthesizeButton.isEnabled = false
        binding.progressBar.visibility = View.GONE
        binding.modelStatus.text = "Kein Modell geladen"
        
        // Einfacher Click Listener
        binding.loadModelButton.setOnClickListener {
            binding.modelStatus.text = "Button wurde geklickt"
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        _binding = null
    }
}
