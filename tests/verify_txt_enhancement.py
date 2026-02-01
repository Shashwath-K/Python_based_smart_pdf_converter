from app.analyzers.structure_scanner import scan_structure, bulletize_text

def test_features():
    with open("sample.txt", "r") as f:
        content = f.read()

    print("--- Testing Auto-Structure ---")
    doc_struct = scan_structure(content, "sample.txt")
    for block in doc_struct.blocks:
        print(f"[{block.type.upper()}]: {block.content[:30]}...")

    print("\n--- Testing Bulletize ---")
    doc_bull = bulletize_text(content, "sample.txt")
    for block in doc_bull.blocks[:3]:
         print(f"[{block.type.upper()}]: {block.content[:30]}...")

if __name__ == "__main__":
    test_features()
