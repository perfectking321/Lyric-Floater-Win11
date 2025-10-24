"""
Test Case 2: Specific Font File Analysis
Check which Segoe UI variant is being loaded and test it
"""
import pygame
import os

pygame.font.init()

print("\n" + "="*60)
print("SEGOE UI FONT VARIANT ANALYSIS")
print("="*60)

# Check all Segoe UI variants
segoe_variants = [
    'segoeui',      # Regular
    'segoeuib',     # Bold
    'segoeuii',     # Italic
    'segoeuil',     # Light
    'segoeuisl',    # Semilight
    'seguiemj',     # Emoji
]

print("\n🔍 Checking Segoe UI variants:")
for variant in segoe_variants:
    path = pygame.font.match_font(variant)
    if path:
        print(f"✅ {variant:15s} -> {path}")
    else:
        print(f"❌ {variant:15s} -> Not found")

# Load the actual font being used
font_path = pygame.font.match_font('segoeui')
print(f"\n📌 Default 'segoeui' resolves to: {font_path}")

# Check file size (Light variant is smaller and may have fewer glyphs)
if font_path and os.path.exists(font_path):
    file_size = os.path.getsize(font_path) / 1024  # KB
    print(f"   File size: {file_size:.1f} KB")
    
    if 'light' in font_path.lower() or 'segoeuil' in font_path.lower():
        print("   ⚠️ WARNING: This is the LIGHT variant!")
        print("   Light variant may have limited Unicode support")
        print("   Should use regular variant (segoeui.ttf)")

# Test Hindi rendering with each variant
print("\n🧪 Testing Hindi rendering with each variant:")
test_text = "आपण सुरू करूया का बाबा"

for variant in ['segoeui', 'segoeuib', None]:
    try:
        if variant:
            path = pygame.font.match_font(variant)
            if not path:
                continue
            font = pygame.font.Font(path, 18)
            label = variant
        else:
            font = pygame.font.Font(None, 18)
            label = "Default (None)"
        
        surface = font.render(test_text, True, (255, 255, 255))
        width = surface.get_width()
        print(f"   {label:15s} -> Width: {width}px {'✅' if width > 100 else '⚠️ Narrow!'}")
    except Exception as e:
        print(f"   {label:15s} -> Error: {e}")

# Recommend fix
print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)

if font_path and 'light' in font_path.lower():
    print("\n❌ PROBLEM FOUND!")
    print("   pygame.font.match_font('segoeui') is loading the LIGHT variant")
    print("   which has limited Devanagari support.")
    
    print("\n🔧 FIX:")
    print("   Update pygame_text_renderer.py to explicitly use regular variant:")
    print()
    print("   # Windows fonts directory")
    print("   font_path = r'C:\\Windows\\Fonts\\segoeui.ttf'  # Regular variant")
    print("   if not os.path.exists(font_path):")
    print("       font_path = pygame.font.match_font('seguisb')  # Semibold")
    print("   if not os.path.exists(font_path):")
    print("       font_path = pygame.font.match_font('nirmalaui')  # Fallback")
else:
    print("\n✅ Font path looks OK")
    print("   Issue might be in how text is being rendered")
    print("   Check antialias settings and color values")
