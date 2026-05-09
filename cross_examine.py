import re
import os
import json

# 1. Get cited keys from main_korean.tex
cited_keys = set()
with open('simple_paper/main_korean.tex', 'r', encoding='utf-8') as f:
    tex_content = f.read()
    cites = re.findall(r'\\cite[a-z]*\{([^}]+)\}', tex_content)
    for cite in cites:
        for k in cite.split(','):
            cited_keys.add(k.strip())

# 2. Get keys and files/titles from references.bib
bib_entries = {}
with open('simple_paper/references.bib', 'r', encoding='utf-8') as f:
    bib_content = f.read()
    
    # Simple parser
    entries = re.split(r'\n@', '\n' + bib_content)[1:]
    for entry in entries:
        lines = entry.split('\n')
        if not lines: continue
        match = re.match(r'^[a-zA-Z]+\{([^,]+),', lines[0])
        if match:
            key = match.group(1).strip()
            
            # Extract title
            title_match = re.search(r'title\s*=\s*[\{"](.*?)(?:[\}"]\s*,|[\}"]\s*\n)', entry, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else "No title found"
            
            # Make it a single line
            title = " ".join(title.split())
            
            # Remove latex brackets from title
            title = title.replace('{', '').replace('}', '')
            
            bib_entries[key] = title

# 3. Get list of PDFs
pdfs = [f for f in os.listdir('papers') if f.endswith('.pdf')]

# Print report
print("=== Cross Examination Report ===")
print(f"Total cited keys in main_korean.tex: {len(cited_keys)}")
print("-" * 40)

missing_in_bib = []
for key in sorted(cited_keys):
    if key not in bib_entries:
        missing_in_bib.append(key)
        print(f"[ERROR] '{key}' is cited but not found in references.bib")
    else:
        title = bib_entries[key]
        # Very simple heuristic matching words from title against PDF names
        # Just to help human review
        print(f"Key: {key}")
        print(f"  Title: {title}")
        
        # Try to find matching PDF (by author name or title keywords)
        author = key.split('20')[0].split('19')[0] # approximate author name from key like 'kim2014nps' -> 'kim'
        
        matches = [p for p in pdfs if author.lower() in p.lower()]
        if not matches:
            print(f"  ? No obvious matching PDF for author '{author}'")
        else:
            print(f"  > Possible PDFs: {matches}")
        print()
