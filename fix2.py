#!/usr/bin/env python3

def fix_main_activity():
    """Korrigiert den Input-Namen für das ONNX Modell"""
    
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "r") as f:
        content = f.read()
    
    # Ersetze den falschen Input-Namen
    content = content.replace(
        """val input = OnnxTensor.createTensor(OrtEnvironment.getEnvironment(), inputTensor, shape)
                
                val output = session.run(mapOf("input" to input))""",
        """val input = OnnxTensor.createTensor(OrtEnvironment.getEnvironment(), inputTensor, shape)
                
                val output = session.run(mapOf("text" to input))"""
    )
    
    with open("app/src/main/java/com/example/ttsapp/MainActivity.kt", "w") as f:
        f.write(content)
    
    print("✅ Input Name korrigiert")

if __name__ == "__main__":
    fix_main_activity()
