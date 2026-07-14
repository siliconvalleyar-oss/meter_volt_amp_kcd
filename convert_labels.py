#!/usr/bin/env python3
"""
Convert global_label to hierarchical_label in KiCad sub-schematic files.
Correctly handles the full global_label structure including all properties.
"""
import re
import os
import uuid

PROJ_DIR = "/Users/bee/Documents/kicad/amper_volt_meter"

def convert_global_to_hierarchical(filepath):
    """Convert all global_label to hierarchical_label in a file"""
    with open(filepath, 'r') as f:
        content = f.read()

    count = 0

    # Pattern to match full global_label block including all nested content
    # global_label has: name, shape, at, fields_autoplaced, effects, uuid, property
    pattern = r'\t\(global_label\s+"([^"]+)"\n(?:\t\t.*?\n)*?\t\)\n'

    def replace_label(match):
        nonlocal count
        name = match.group(1)
        full_block = match.group(0)

        # Extract key properties from the global_label
        shape_match = re.search(r'\(shape\s+(\w+)\)', full_block)
        at_match = re.search(r'\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)', full_block)

        shape = shape_match.group(1) if shape_match else "bidirectional"
        at_x = at_match.group(1) if at_match else "0"
        at_y = at_match.group(2) if at_match else "0"
        at_rot = at_match.group(3) if at_match else "0"

        # Map global_label shapes to hierarchical_label shapes
        # global: input/output/bidirectional/power_in/power_out
        # hierarchical: input/output/bidirectional/tristate
        if shape in ("power_in", "power_out"):
            shape = "bidirectional"

        new_label = f'\t(hierarchical_label\n'
        new_label += f'\t\t(name "{name}")\n'
        new_label += f'\t\t(shape {shape})\n'
        new_label += f'\t\t(at {at_x} {at_y} {at_rot})\n'
        new_label += f'\t\t(fields_autoplaced yes)\n'
        new_label += f'\t\t(effects\n'
        new_label += f'\t\t\t(font\n'
        new_label += f'\t\t\t\t(size 1.27 1.27)\n'
        new_label += f'\t\t\t)\n'
        new_label += f'\t\t)\n'
        new_label += f'\t\t(uuid "{str(uuid.uuid4())}")\n'
        new_label += f'\t)\n'

        count += 1
        return new_label

    new_content = re.sub(pattern, replace_label, content, flags=re.DOTALL)

    if count > 0:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return count
    return 0

def main():
    print("=== Convirtiendo global_label a hierarchical_label ===\n")

    total = 0
    for f in os.listdir(PROJ_DIR):
        if f.endswith('.kicad_sch') and f != 'amper_volt_meter.kicad_sch':
            filepath = os.path.join(PROJ_DIR, f)
            with open(filepath, 'r') as fh:
                content = fh.read()
            if 'global_label' in content:
                count = convert_global_to_hierarchical(filepath)
                if count > 0:
                    print(f"  {f}: {count} etiquetas convertidas")
                    total += count

    print(f"\nTotal: {total} etiquetas convertidas")

if __name__ == "__main__":
    main()
