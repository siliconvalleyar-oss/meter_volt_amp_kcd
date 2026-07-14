#!/usr/bin/env python3
"""
Script para remover hierarchical_label del schematic principal
Los pines se generan automáticamente desde los sub-schematics
"""
import re
import os

PROJ_DIR = "/Users/bee/Documents/kicad/amper_volt_meter"

def remove_hierarchical_labels_from_main(content):
    """Remueve todos los hierarchical_label del schematic principal"""
    # Pattern to match hierarchical_label blocks with various indentation levels
    pattern = r'\n\t+\(hierarchical_label\s*\n(?:\t+\(.*?\)\n)+?\t+\)\n'

    count = len(re.findall(pattern, content, re.DOTALL))
    content = re.sub(pattern, '\n', content)

    # Also try a simpler pattern for single-line or different formatting
    pattern2 = r'\n\t+\(hierarchical_label\s+\(name\s+"[^"]+"\)\s+\(shape\s+\w+\)\s+\(at\s+[\d.]+\s+[\d.]+\s+\d+\)\s+\(fields_autoplaced\s+\w+\)\s+\(effects\s+\(font\s+\(size\s+[\d.]+\s+[\d.]+\)\)\)\s+\(uuid\s+"[^"]+"\)\)\n'
    count2 = len(re.findall(pattern2, content))
    content = re.sub(pattern2, '\n', content)

    return content, count + count2

def main():
    print("=== Removiendo hierarchical_label del schematic principal ===\n")

    main_sch = os.path.join(PROJ_DIR, "amper_volt_meter.kicad_sch")

    with open(main_sch, 'r') as f:
        content = f.read()

    print(f"Etiquetas antes: {content.count('hierarchical_label')}")

    content, count = remove_hierarchical_labels_from_main(content)

    print(f"Etiquetas removidas: {count}")
    print(f"Etiquetas después: {content.count('hierarchical_label')}")

    with open(main_sch, 'w') as f:
        f.write(content)

    print("\nSchematic principal limpiado")

if __name__ == "__main__":
    main()
