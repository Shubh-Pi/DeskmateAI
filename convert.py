# convert.py
import os

model_path = os.path.abspath("NLP/models/whisper_safetensors_backup")
output_path = os.path.abspath("NLP/models/whisper_small_converted")

print(f"[CONVERT] Input:  {model_path}")
print(f"[CONVERT] Output: {output_path}")
print("[CONVERT] Converting whisper-small safetensors → CTranslate2 int8...")
print("[CONVERT] Please wait (3-5 minutes)...")

try:
    from ctranslate2.converters import TransformersConverter

    converter = TransformersConverter(model_path)
    converter.convert(
        output_path,
        quantization="int8",
        force=True
    )

    print("\n[CONVERT] Conversion successful!")
    print("[CONVERT] Output files:")
    for f in os.listdir(output_path):
        size = os.path.getsize(os.path.join(output_path, f))
        print(f"  - {f} ({size // 1024} KB)")

    # Backup old folder and replace with converted
    import shutil
    backup = os.path.abspath("NLP/models/whisper_safetensors_backup")
    shutil.copytree(model_path, backup)
    print(f"\n[CONVERT] Backup saved to: {backup}")
    
    # Replace whisper folder with converted files
    shutil.rmtree(model_path)
    shutil.copytree(output_path, model_path)
    shutil.rmtree(output_path)
    
    print("[CONVERT] Done! NLP/models/whisper now has CTranslate2 model.")
    print("[CONVERT] Run python main.py to test.")

except Exception as e:
    print(f"\n[CONVERT] Error: {e}")
    import traceback
    traceback.print_exc()