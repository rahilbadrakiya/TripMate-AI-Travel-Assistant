import os
import zipfile

def create_zip(source_dir, output_filename):
    # Files/Dirs to exclude
    EXCLUDE_DIRS = {'.venv', 'venv', '__pycache__', '.git', '.idea', 'env'}
    EXCLUDE_FILES = {'tripmate.db', '.env', '.DS_Store', output_filename}
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                if file.endswith('.pyc'):
                    continue
                    
                file_path = os.path.join(root, file)
                # Archive name should be relative to source_dir
                arcname = os.path.relpath(file_path, source_dir)
                
                print(f"Adding {arcname}...")
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    source = os.path.dirname(os.path.abspath(__file__))
    output = os.path.join(source, 'backend_deploy.zip')
    create_zip(source, output)
    print(f"\nSuccessfully created deployment zip: {output}")
