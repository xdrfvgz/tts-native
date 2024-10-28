#!/usr/bin/env python3

def fix_loader_complete():
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "r") as f:
        content = f.read()
    
    # Finde und ersetze die loadExternalModel Funktion
    old_function = """    private fun loadExternalModel(uri: Uri) {
        lifecycleScope.launch(Dispatchers.IO) {
            updateUIState(isLoading = true)

            try {
                val modelBytes = contentResolver.openInputStream(uri)?.use { it.readBytes() }
                    ?: throw Exception("Konnte Modelldatei nicht lesen")

                loadModelFromBytes(modelBytes)
                updateModelStatus("Externes Modell aktiv")
            } catch (e: Exception) {
                showToast("Modelladung fehlgeschlagen: ${e.message}")
            } finally {
                updateUIState(isLoading = false)
            }
        }
    }"""

    new_function = """    private fun loadExternalModel(uri: Uri) {
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
                updateModelStatus("Externes Modell aktiv")
            } catch (e: Exception) {
                showToast("Modelladung fehlgeschlagen: ${e.message}")
            } finally {
                withContext(Dispatchers.Main) {
                    binding.loadModelButton.isEnabled = true
                    binding.progressBar.visibility = android.view.View.GONE
                }
            }
        }
    }"""

    content = content.replace(old_function, new_function)
    
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "w") as f:
        f.write(content)
    
    print("✅ loadExternalModel komplett überarbeitet")

if __name__ == "__main__":
    fix_loader_complete()
