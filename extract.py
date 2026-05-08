import fitz
import os
import glob

pdf_files = glob.glob('papers/*.pdf')

for pdf_path in pdf_files:
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    out_dir = f'papers/{base_name.replace(" ", "_")}_assets'
    os.makedirs(out_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    text_out = []
    
    for i, page in enumerate(doc):
        text = page.get_text("text")
        text_out.append(f"--- PAGE {i+1} ---\n{text}")
        
        # Extract images
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            img_filename = f"page{i+1}_img{img_index}.{image_ext}"
            img_filepath = os.path.join(out_dir, img_filename)
            with open(img_filepath, "wb") as f:
                f.write(image_bytes)
                
            text_out.append(f"\n[IMAGE EXTRACTED: {img_filepath}]\n")
            
    with open(f'papers/{base_name.replace(" ", "_")}_raw_text.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(text_out))
    print(f"Processed {pdf_path}")
