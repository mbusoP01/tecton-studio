import os
import zipfile
import io

def create_zip_from_folder(folder_path):
    """Compresses a folder into a ZIP file in memory."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zip_file.write(file_path, arcname)
    buffer.seek(0)
    return buffer

def save_file(base_path, filename, content):
    """Saves content to a file, creating folders as needed."""
    full_path = os.path.join(base_path, filename)
    directory = os.path.dirname(full_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return full_path

def read_file(base_path, filename):
    """Reads content safely."""
    full_path = os.path.join(base_path, filename)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def scan_directory(base_path):
    """Returns list of files."""
    file_list = []
    if not os.path.exists(base_path):
        return []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), base_path)
            file_list.append(rel_path.replace("\\", "/"))
    return file_list

def assemble_preview_html(base_path):
    """
    Smart Assembler: Finds index.html and injects the local CSS/JS 
    so the preview works without an external server.
    """
    if not os.path.exists(base_path):
        return None
        
    # 1. Find the main HTML file
    html_content = ""
    if os.path.exists(os.path.join(base_path, "index.html")):
        html_content = read_file(base_path, "index.html")
    else:
        # Fallback: look for any html file
        files = scan_directory(base_path)
        html_files = [f for f in files if f.endswith(".html")]
        if html_files:
            html_content = read_file(base_path, html_files[0])
        else:
            return "<h3>Waiting for HTML generation...</h3>"

    # 2. Find and Inject CSS (Simple heuristic)
    # We look for <link rel="stylesheet" href="style.css"> and replace it with actual CSS
    files = scan_directory(base_path)
    css_files = [f for f in files if f.endswith(".css")]
    
    for css_file in css_files:
        css_content = read_file(base_path, css_file)
        # Robust replacement: try to find the link tag, or just append to head
        if css_file in html_content:
            # Replace standard link tag
            # Note: This is a basic string replace, robust enough for AI code
            html_content = html_content.replace(f'<link rel="stylesheet" href="{css_file}">', f'<style>{css_content}</style>')
            html_content = html_content.replace(f'<link rel="stylesheet" href="./{css_file}">', f'<style>{css_content}</style>')
        else:
            # If not found, just inject into head
            html_content = html_content.replace("</head>", f"<style>{css_content}</style></head>")

    # 3. Find and Inject JS
    js_files = [f for f in files if f.endswith(".js")]
    for js_file in js_files:
        js_content = read_file(base_path, js_file)
        if js_file in html_content:
            html_content = html_content.replace(f'<script src="{js_file}"></script>', f'<script>{js_content}</script>')
            html_content = html_content.replace(f'<script src="./{js_file}"></script>', f'<script>{js_content}</script>')
        else:
            html_content = html_content.replace("</body>", f"<script>{js_content}</script></body>")
            
    return html_content