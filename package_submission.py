#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import zipfile

def package_submission():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sub_dir = os.path.join(base_dir, "submission")
    zip_path = os.path.join(base_dir, "EDA_Competition_Case7_Final_Submission.zip")
    
    if not os.path.exists(sub_dir):
        print(f"Error: {sub_dir} does not exist.")
        sys.exit(1)
        
    print(f"Packaging submission files from: {sub_dir}")
    print(f"Target archive: {zip_path}")
    
    file_count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(sub_dir):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file, sub_dir)
                zipf.write(abs_file, os.path.join("EDA_Competition_Case7_Final_Submission", rel_path))
                file_count += 1
                print(f"  + Added: {rel_path}")
                
    zip_size_kb = os.path.getsize(zip_path) / 1024.0
    print(f"\nSuccessfully packaged {file_count} files into:")
    print(f"  -> {zip_path} ({zip_size_kb:.2f} KB)\n")

if __name__ == "__main__":
    package_submission()
