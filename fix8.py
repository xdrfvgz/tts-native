// app/build.gradle
android {
    // ... andere Konfigurationen bleiben gleich ...

    sourceSets {
        main {
            assets {
                srcDirs = ['src/main/assets']
                aaptOptions {
                    noCompress 'onnx'  // Verhindert Kompression der ONNX Dateien
                }
            }
        }
    }
}
