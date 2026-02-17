"""
Script to download NELFUND documents from official sources
Run this script to fetch and save NELFUND documents to the data folder
"""
import os
import requests
from pathlib import Path

# Get paths
BACKEND_DIR = Path(__file__).parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "nelfund_docs"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Known NELFUND document URLs (update these with actual URLs when available)
NELFUND_DOCUMENTS = {
    # Official Act
    "Student_Loan_Act_2023.pdf": "https://www.nelf.gov.ng/documents/act-2023.pdf",  # Placeholder - update with real URL
    
    # Official Guidelines
    "NELFUND_Official_Guidelines.pdf": "https://www.nelf.gov.ng/documents/guidelines.pdf",  # Placeholder
    
    # Application Procedures
    "Application_Procedures.pdf": "https://www.nelf.gov.ng/documents/application-procedures.pdf",  # Placeholder
    
    # FAQs
    "NELFUND_FAQs.pdf": "https://www.nelf.gov.ng/documents/faqs.pdf",  # Placeholder
    
    # Covered Institutions
    "Covered_Institutions_List.pdf": "https://www.nelf.gov.ng/documents/institutions.pdf",  # Placeholder
}

def download_file(url: str, filepath: Path) -> bool:
    """Download a file from URL to filepath"""
    try:
        print(f"Downloading {filepath.name}...")
        response = requests.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Successfully downloaded {filepath.name}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {filepath.name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error saving {filepath.name}: {e}")
        return False

def main():
    print("=" * 60)
    print("NELFUND Document Downloader")
    print("=" * 60)
    print(f"Target directory: {DATA_DIR}")
    print()
    
    downloaded = 0
    failed = 0
    
    for filename, url in NELFUND_DOCUMENTS.items():
        filepath = DATA_DIR / filename
        
        # Skip if file already exists
        if filepath.exists():
            print(f"⏭️  {filename} already exists, skipping...")
            continue
        
        if download_file(url, filepath):
            downloaded += 1
        else:
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Download complete: {downloaded} downloaded, {failed} failed")
    print(f"Total files in data folder: {len(list(DATA_DIR.glob('*')))}")
    print("=" * 60)
    
    if failed > 0:
        print("\n⚠️  Some downloads failed. You may need to:")
        print("1. Check the URLs in this script are correct")
        print("2. Visit https://www.nelf.gov.ng manually to download documents")
        print("3. Place downloaded PDFs in the data/nelfund_docs folder")

if __name__ == "__main__":
    # Install requests if not available
    try:
        import requests
    except ImportError:
        print("Installing requests library...")
        os.system("pip install requests")
        import requests
    
    main()

