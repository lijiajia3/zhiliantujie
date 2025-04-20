import os
import re


EXTENSIONS = [".py", ".js", ".jsx", ".css"]


def remove_comments(content, ext):
    if ext == ".py":
        
        content = re.sub(r"", "", content)
        content = re.sub(r'', "", content)
        
        content = re.sub(r'
    else:
        
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        
        content = re.sub(r'//.*', '', content)
    return content


def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in EXTENSIONS:
                full_path = os.path.join(root, file)
                print(f"🚀 清理注释: {full_path}")
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                cleaned = remove_comments(content, ext)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(cleaned)

if __name__ == "__main__":
    target_directory = "./"  
    process_directory(target_directory)