#!/usr/bin/env python3

def fix_loader():
    """Korrigiert den loadExternalModel Call"""
    
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "r") as f:
        content = f.read()

    # Ersetze die problematische Methode
    content = content.replace(
        """    private fun loadExternalModel(uri: Uri) {
        updateUIState(isLoading = true)

        lifecycleScope.launch(Dispatchers.IO) {""",
        """    private fun loadExternalModel(uri: Uri) {
        lifecycleScope.launch(Dispatchers.IO) {
            updateUIState(isLoading = true)""")

    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "w") as f:
        f.write(content)

    print("✅ Loader-Methode korrigiert")

if __name__ == "__main__":
    fix_loader()
