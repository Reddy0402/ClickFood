import os
import re

templates_dir = r'c:\Users\vippa\Downloads\fooddelivery\fooddelivery\orders\templates'
files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]

def refine_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix cart icon color on light background
    content = content.replace("color: #fff;\" onmouseover=\"this.style.background='rgba(255,255,255,0.3)'", "color: #fff;\"") # safeguard for home.html
    
    # If a button has #f5f5f5 background, icon should be dark
    content = re.sub(r'background:\s*#f5f5f5;.*?color:\s*#fff;', lambda m: m.group(0).replace('#fff', '#0f172a'), content, flags=re.DOTALL)
    
    # Fix the subtitle color in the header
    content = content.replace('color: #221f1f;', 'color: #94a3b8;')
    
    # Fix the header title font weight for all pages
    content = content.replace('font-size: 2.2rem; color: #fff;', 'font-size: 2.2rem; color: #fff; font-weight: 800; letter-spacing: -1px;')
    
    # Unify the header logo HTML structure across all pages
    content = content.replace('ClickFood Premium</h1>', 'ClickFood <span style="font-weight:300; color:#94a3b8;">Premium</span></h1>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for filename in files:
    refine_file(os.path.join(templates_dir, filename))

print("Refined contrast and branding across all templates.")
