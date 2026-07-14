#!/usr/bin/env python3
"""
Script para corregir la posición de los pines jerárquicos en el schematic principal
"""
import re
import os
import uuid

PROJ_DIR = "/Users/bee/Documents/kicad/amper_volt_meter"

def get_sheet_uuids():
    """Obtiene los UUIDs de cada sheet"""
    main_sch = os.path.join(PROJ_DIR, "amper_volt_meter.kicad_sch")
    with open(main_sch, 'r') as f:
        content = f.read()

    sheets = {}
    sheet_pattern = r'\(sheet\s.*?\(uuid\s+"([^"]+)"\).*?\(property\s+"Sheetname"\s+"([^"]+)".*?\(property\s+"Sheetfile"\s+"([^"]+)"'
    for match in re.finditer(sheet_pattern, content, re.DOTALL):
        uuid_val = match.group(1)
        name = match.group(2)
        filename = match.group(3)
        sheets[name] = {'uuid': uuid_val, 'file': filename}

    return sheets

def get_hierarchical_labels(sch_file):
    """Obtiene las etiquetas jerárquicas de un sub-schematic"""
    with open(sch_file, 'r') as f:
        content = f.read()

    labels = []
    pattern = r'\(hierarchical_label\s*\n\s*\(name\s+"([^"]+)"\)'
    for match in re.finditer(pattern, content):
        name = match.group(1)
        start_pos = match.end()
        pos_pattern = r'\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)'
        pos_match = re.search(pos_pattern, content[start_pos:start_pos+500])
        if pos_match:
            labels.append({
                'name': name,
                'x': float(pos_match.group(1)),
                'y': float(pos_match.group(2)),
                'rotation': int(pos_match.group(3))
            })
    return labels

def remove_hierarchical_labels(content):
    """Remueve todas las etiquetas jerárquicas mal colocadas"""
    # Pattern to match hierarchical_label blocks with incorrect indentation
    pattern = r'\n\t\t\t\(hierarchical_label.*?\n\t\t\t\)\n'
    content = re.sub(pattern, '\n', content)
    # Also try with different indentation
    pattern2 = r'\n\t\t\(hierarchical_label.*?\n\t\t\)\n'
    content = re.sub(pattern2, '\n', content)
    return content

def add_pins_correctly(content, sheet_uuid, labels):
    """Agrega pines jerárquicos en la posición correcta"""
    if not labels:
        return content

    # Build the hierarchical labels block with correct indentation
    labels_block = ""
    for label in labels:
        label_uuid = str(uuid.uuid4())
        x = label['x']
        y = label['y']
        rotation = label['rotation']

        labels_block += f"\t\t(hierarchical_label\n"
        labels_block += f"\t\t\t(name \"{label['name']}\")\n"
        labels_block += f"\t\t\t(shape bidirectional)\n"
        labels_block += f"\t\t\t(at {x} {y} {rotation})\n"
        labels_block += f"\t\t\t(fields_autoplaced yes)\n"
        labels_block += f"\t\t\t(effects\n"
        labels_block += f"\t\t\t\t(font\n"
        labels_block += f"\t\t\t\t\t(size 1.27 1.27)\n"
        labels_block += f"\t\t\t\t)\n"
        labels_block += f"\t\t\t)\n"
        labels_block += f"\t\t\t(uuid \"{label_uuid}\")\n"
        labels_block += f"\t\t)\n"

    # Find the sheet and insert labels before (instances
    sheet_pattern = rf'(\(sheet\s.*?\(uuid\s+"{sheet_uuid}"\).*?)(\(instances)'

    def insert_labels(match):
        sheet_part = match.group(1)
        instances_part = match.group(2)
        return sheet_part + labels_block + "\t\t" + instances_part

    content = re.sub(sheet_pattern, insert_labels, content, count=1, flags=re.DOTALL)

    return content

def main():
    print("=== Corrigiendo pines jerárquicos ===\n")

    sheets = get_sheet_uuids()
    main_sch = os.path.join(PROJ_DIR, "amper_volt_meter.kicad_sch")

    with open(main_sch, 'r') as f:
        content = f.read()

    # Remove incorrectly placed hierarchical labels
    print("Removiendo etiquetas mal colocadas...")
    content = remove_hierarchical_labels(content)

    total_pins = 0

    for sheet_name, sheet_info in sheets.items():
        sch_file = os.path.join(PROJ_DIR, sheet_info['file'])

        if not os.path.exists(sch_file):
            continue

        labels = get_hierarchical_labels(sch_file)

        if not labels:
            print(f"  {sheet_name}: Sin etiquetas")
            continue

        print(f"  {sheet_name}: {len(labels)} pines")
        content = add_pins_correctly(content, sheet_info['uuid'], labels)
        total_pins += len(labels)

    with open(main_sch, 'w') as f:
        f.write(content)

    print(f"\nTotal: {total_pins} pines corregidos")

if __name__ == "__main__":
    main()
