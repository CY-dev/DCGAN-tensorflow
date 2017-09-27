import zipfile

def unzip_and_save(source_path, target_path):
    zip_ref = zipfile.ZipFile(source_path, 'r')
    zip_ref.extractall(target_path)
    zip_ref.close()
