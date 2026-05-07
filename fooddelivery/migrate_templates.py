import os
import re

templates_dir = r'c:\Users\vippa\Downloads\fooddelivery\fooddelivery\orders\templates'
files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]

replacements = {
    '#fff6f6': '#f8fafc',
    '#f06666': '#0f172a',
    '#ff6f61': '#0f172a',
    '#ffe0e0': '#e2e8f0',
    '#fff0f0': '#f1f5f9',
    'Dhee Quick Bites': 'ClickFood Premium',
    'click food': 'ClickFood Premium',
    'linear-gradient(135deg, #f06666, #ff4b4b)': '#0f172a',
    'box-shadow: 0 4px 15px rgba(240, 102, 102, 0.3)': 'box-shadow: 0 4px 20px rgba(0,0,0,0.4)',
    'box-shadow: 0 2px 12px rgba(240,102,102,0.08)': 'box-shadow: 0 10px 30px rgba(0,0,0,0.1)',
    'background: #222': 'background: #0f172a',
    'color: #222': 'color: #fff',
}

def migrate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple string replacements
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Specific fix for headers if they are still red
    content = re.sub(r'background:\s*#f06666', 'background: #0f172a', content)
    
    # Fix body font if it's still Segoe UI
    content = content.replace("'Segoe UI', Arial, sans-serif", "'Inter', sans-serif")
    
    # Fix the header logo area consistency
    header_pattern = r'<header style="background: #0f172a;[^>]*>.*?<h1>.*?</h1>'
    def header_sub(match):
        return match.group(0).replace('color: #fff', 'color: #fff').replace('font-weight: 700', 'font-weight: 800')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for filename in files:
    migrate_file(os.path.join(templates_dir, filename))

print(f"Migrated {len(files)} template files to the premium theme.")
