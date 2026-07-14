#!/usr/bin/env python3
"""
Fix hierarchical_label indentation in sub-schematic files.
In KiCad schematics, hierarchical_label is a top-level element (1 tab indent),
with children at 2 tabs indent.
"""
import re
import os

PROJ_DIR = "/Users/bee/Documents/kicad/amper_volt_meter"

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Find all hierarchical_label blocks and fix their indentation
    # Current broken format: \t\t(hierarchical_label\n\t\t(name...\n
    # Correct format: \t(hierarchical_label\n\t\t(name...\n

    # Match hierarchical_label blocks at wrong indentation
    pattern = r'(\t+)\(hierarchical_label\n(.*?)\n(\t+)\)'

    def fix_match(m):
        indent = '\t'
        inner = m.group(2)
        # Fix inner indentation: each line should start with \t\t
        lines = inner.split('\n')
        fixed_lines = []
        for line in lines:
            stripped = line.lstrip('\t')
            fixed_lines.append('\t\t' + stripped)
        fixed_inner = '\n'.join(fixed_lines)
        return f'{indent}(hierarchical_label\n{fixed_inner}\n{indent})'

    new_content = re.sub(pattern, fix_match, content, flags=re.DOTALL)

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    return False

def main():
    for f in os.listdir(PROJ_DIR):
        if f.endswith('.kicad_sch') and f != 'amper_volt_meter.kicad_sch':
            filepath = os.path.join(PROJ_DIR, f)
            if 'hierarchical_label' in open(filepath).read():
                if fix_file(filepath):
                    print(f'Fixed: {f}')
                else:
                    print(f'OK: {f}')

if __name__ == "__main__":
    main()
