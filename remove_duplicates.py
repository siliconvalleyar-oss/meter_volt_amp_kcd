#!/usr/bin/env python3
"""
Script para remover pines jerárquicos duplicados
"""
import re
import os

PROJ_DIR = "/Users/bee/Documents/kicad/amper_volt_meter"

def remove_duplicate_labels(content):
    """Remueve etiquetas jerárquicas duplicadas"""
    # Find all hierarchical_label blocks
    pattern = r'\(hierarchical_label\s*\n\s*\(name\s+"([^"]+)"\).*?\(uuid\s+"([^"]+)"\)\s*\)'

    seen_labels = {}
    labels_to_remove = []

    for match in re.finditer(pattern, content, re.DOTALL):
        name = match.group(1)
        uuid_val = match.group(2)
        start = match.start()
        end = match.end()

        if name in seen_labels:
            # Duplicate found - mark for removal
            labels_to_remove.append((start, end))
            print(f"  Duplicado: {name} (uuid: {uuid_val})")
        else:
            seen_labels[name] = uuid_val

    # Remove duplicates in reverse order to maintain positions
    for start, end in reversed(labels_to_remove):
        content = content[:start] + content[end:]

    return content, len(labels_to_remove)

def main():
    print("=== Removiendo pines jerárquicos duplicados ===\n")

    main_sch = os.path.join(PROJ_DIR, "amper_volt_meter.kicad_sch")

    with open(main_sch, 'r') as f:
        content = f.read()

    content, count = remove_duplicate_labels(content)

    with open(main_sch, 'w') as f:
        f.write(content)

    print(f"\nRemovidos {count} pines duplicados")

if __name__ == "__main__":
    main()
