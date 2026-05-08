import re

with open('papers/What_Really_Explains_the_Korea_Discount_and_PBR_raw_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace image tags
text = re.sub(r'\[IMAGE EXTRACTED: papers/What_Really_Explains_the_Korea_Discount_and_PBR_assets/(.*?)\]', r'![Figure](./What_Really_Explains_the_Korea_Discount_and_PBR_assets/\1)', text)

with open('papers/What_Really_Explains_the_Korea_Discount_and_PBR.md', 'w', encoding='utf-8') as f:
    f.write(text)
