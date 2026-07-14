#!/usr/bin/env python3
"""
Convert global_label to hierarchical_label in KiCad schematic files.
Properly handles the full S-expression structure.
"""
import re
import os
import uuid

PROJ_DIR = "/Users/bee/Documents/kicad/amper_volt_meter"

def find_balanced_paren(content, start):
    """Find the matching closing paren for an opening paren at position start"""
    depth = 0
    for i in range(start, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1

def convert_global_to_hierarchical(filepath):
    """Convert all global_label to hierarchical_label in a file"""
    with open(filepath, 'r') as f:
        content = f.read()

    count = 0
    result = []
    i = 0

    while i < len(content):
        # Look for global_label
        match = re.search(r'\(global_label\s+"', content[i:])
        if not match:
            result.append(content[i:])
            break

        # Add content before the match
        result.append(content[i:i + match.start()])

        # Find the full block
        block_start = i + match.start()
        block_end = find_balanced_paren(content, block_start)

        if block_end == -1:
            # Can't find end, just add the rest
            result.append(content[block_start:])
            break

        block = content[block_start:block_end + 1]

        # Extract properties
        name_match = re.search(r'\(global_label\s+"([^"]+)"', block)
        shape_match = re.search(r'\(shape\s+(\w+)\)', block)
        at_match = re.search(r'\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)', block)

        name = name_match.group(1) if name_match else "unknown"
        shape = shape_match.group(1) if shape_match else "bidirectional"
        at_x = at_match.group(1) if at_match else "0"
        at_y = at_match.group(2) if at_match else "0"
        at_rot = at_match.group(3) if at_match else "0"

        # Map shapes
        shape_map = {
            "power_in": "bidirectional",
            "power_out": "bidirectional",
            "input": "input",
            "output": "output",
            "bidirectional": "bidirectional",
            "tri_state": "tri_state",
            "passive": "passive",
        }
        shape = shape_map.get(shape, "bidirectional")

        # Build hierarchical_label
        new_label = f'(hierarchical_label\n'
        new_label += f'\t(name "{name}")\n'
        new_label += f'\t(shape {shape})\n'
        new_label += f'\t(at {at_x} {at_y} {at_rot})\n'
        new_label += f'\t(fields_autoplaced yes)\n'
        new_label += f'\t(effects\n'
        new_label += f'\t\t(font\n'
        new_label += f'\t\t\t(size 1.27 1.27)\n'
        new_label += f'\t\t)\n'
        new_label += f'\t)\n'
        new_label += f'\t(uuid "{str(uuid.uuid4())}")\n'
        new_label += f')'

        result.append(new_label)

        i = block_end + 1
        count += 1

    if count > 0:
        new_content = ''.join(result)
        with open(filepath, 'w') as f:
            f.write(new_content)
        return count
    return 0

def main():
    print("=== Convirtiendo global_label a hierarchical_label ===\n")

    total = 0
    for f in sorted(os.listdir(PROJ_DIR)):
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
