#!/usr/bin/env python3

def fix_main_activity():
    """Korrigiert die Fehler in der MainActivity.kt"""
    
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "r") as f:
        content = f.read()

    # 1. BUFFER_SIZE aus companion object raus
    content = content.replace(
        """companion object {
        private const val SAMPLE_RATE = 22050 // Standard TTS sample rate
        private const val PERMISSION_REQUEST_CODE = 1001
        private const val BUFFER_SIZE = AudioTrack.getMinBufferSize(
            SAMPLE_RATE,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_FLOAT
        )
    }""",
        """companion object {
        private const val SAMPLE_RATE = 22050 // Standard TTS sample rate
        private const val PERMISSION_REQUEST_CODE = 1001
    }

    private val BUFFER_SIZE = AudioTrack.getMinBufferSize(
        SAMPLE_RATE,
        AudioFormat.CHANNEL_OUT_MONO,
        AudioFormat.ENCODING_PCM_FLOAT
    )""")

    # 2. setupListeners Coroutine Fix
    content = content.replace(
        """binding.synthesizeButton.setOnClickListener {
            if (!isProcessing) {
                val text = binding.inputText.text?.toString() ?: ""
                if (text.isNotEmpty()) {
                    synthesizeText(text)
                } else {
                    showToast("Bitte Text eingeben")
                }
            }
        }""",
        """binding.synthesizeButton.setOnClickListener {
            if (!isProcessing) {
                val text = binding.inputText.text?.toString() ?: ""
                if (text.isNotEmpty()) {
                    synthesizeText(text)
                } else {
                    lifecycleScope.launch {
                        showToast("Bitte Text eingeben")
                    }
                }
            }
        }""")

    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "w") as f:
        f.write(content)

    print("✅ MainActivity.kt Fehler behoben")

if __name__ == "__main__":
    fix_main_activity()
