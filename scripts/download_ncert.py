import os
import requests
from pathlib import Path

# Target directories
PROJECT_ROOT = Path(__file__).parent.parent
NCERT_DIR = PROJECT_ROOT / "data" / "ncert"

# NCERT download targets (Class 9 and 10 Science chapters)
# jesc106.pdf is Class 10 Science Chapter 6 (Life Processes - Photosynthesis)
# iesc101.pdf is Class 9 Science Chapter 1 (Matter in Our Surroundings)
CHAPTERS = {
    "class10_science_ch6_photosynthesis.pdf": "https://ncert.nic.in/textbook/pdf/jesc106.pdf",
    "class9_science_ch1_states_of_matter.pdf": "https://ncert.nic.in/textbook/pdf/iesc101.pdf",
}

# Standard web browser User-Agent to prevent bot-blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_file(url: str, dest_path: Path):
    """Downloads a file with stream visualization."""
    print(f"Downloading from: {url}")
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        response.raise_for_status()
        
        # Write chunks
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Successfully saved to: {dest_path}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def main():
    print("=================================================================")
    print("                 Genius NCERT PDF Downloader")
    print("=================================================================")
    print()
    
    # Create target folder
    os.makedirs(NCERT_DIR, exist_ok=True)
    
    success_count = 0
    for filename, url in CHAPTERS.items():
        dest = NCERT_DIR / filename
        if dest.exists() and dest.stat().st_size > 10000:
            print(f"File already exists (skipping): {filename}")
            success_count += 1
            continue
            
        success = download_file(url, dest)
        if success:
            success_count += 1
            
    print()
    print(f"Download process finished. {success_count}/{len(CHAPTERS)} files ready.")
    
    if success_count > 0:
        print("Initializing vector database indexing...")
        # Add project root to path to import genius package
        import sys
        sys.path.append(str(PROJECT_ROOT))
        
        from genius.ai.rag import build_vector_index
        build_vector_index()
    else:
        print("[Warning] No PDFs could be downloaded. RAG will operate in offline/keyword-search fallback mode.")

if __name__ == "__main__":
    main()
