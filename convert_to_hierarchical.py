#!/usr/bin/env python3
"""
Script para convertir etiquetas globales a pines jerárquicos en KiCad
"""
import re
import os
import uuid

PROJ_DIR = "/Users/bee/Documents/kicad/amper_volt_meter"

def get_sheet_uuids():
    """Obtiene los UUIDs de cada sheet del schematic principal"""
    main_sch = os.path.join(PROJ_DIR, "amper_volt_meter.kicad_sch")
    with open(main_sch, 'r') as f:
        content = f.read()

    sheets = {}
    # Find all sheet definitions with their UUIDs and names
    sheet_pattern = r'\(sheet\s.*?\(uuid\s+"([^"]+)"\).*?\(property\s+"Sheetname"\s+"([^"]+)".*?\(property\s+"Sheetfile"\s+"([^"]+)"'
    for match in re.finditer(sheet_pattern, content, re.DOTALL):
        uuid_val = match.group(1)
        name = match.group(2)
        filename = match.group(3)
        sheets[name] = {'uuid': uuid_val, 'file': filename}

    return sheets

def get_global_labels(sch_file):
    """Obtiene todas las etiquetas globales de un archivo schematic"""
    with open(sch_file, 'r') as f:
        content = f.read()

    labels = []
    pattern = r'\(global_label\s+"([^"]+)"\s.*?\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)'
    for match in re.finditer(pattern, content, re.DOTALL):
        labels.append({
            'name': match.group(1),
            'x': float(match.group(2)),
            'y': float(match.group(3)),
            'rotation': int(match.group(4))
        })
    return labels

def generate_hierarchical_pin(label, pin_uuid):
    """Genera un pin jerárquico para el schematic principal"""
    # Calculate position on sheet (offset from sheet origin)
    return f"""	(hierarchical_label
		(name "{label['name']}")
		(shape bidirectional)
		(at {label['x']} {label['y']} {label['rotation']})
		(fields_autoplaced yes)
		(effects
			(font
				(size 1.27 1.27)
			)
		)
		(uuid "{pin_uuid}")
	)"""

def generate_hierarchical_label(label, label_uuid):
    """Genera una etiqueta jerárquica para el sub-schematic"""
    return f"""	(hierarchical_label
		(name "{label['name']}")
		(shape bidirectional)
		(at {label['x']} {label['y']} {label['rotation']})
		(fields_autoplaced yes)
		(effects
			(font
				(size 1.27 1.27)
			)
		)
		(uuid "{label_uuid}")
	)"""

def convert_sheet(sheet_name, sheet_info):
    """Convierte las etiquetas globales de un sheet a pines jerárquicos"""
    sch_file = os.path.join(PROJ_DIR, sheet_info['file'])

    if not os.path.exists(sch_file):
        print(f"  Archivo no encontrado: {sch_file}")
        return

    labels = get_global_labels(sch_file)
    if not labels:
        print(f"  No hay etiquetas globales")
        return

    print(f"  Encontradas {len(labels)} etiquetas globales")

    # Read the sub-schematic
    with open(sch_file, 'r') as f:
        content = f.read()

    # Replace global labels with hierarchical labels
    for label in labels:
        old_pattern = rf'\(global_label\s+"{re.escape(label["name"])}"\s.*?\(at\s+{label["x"]}\s+{label["y"]}\s+{label["rotation"]}\)'
        new_label = generate_hierarchical_label(label, str(uuid.uuid4()))
        content = re.sub(old_pattern, new_label, content, count=1, flags=re.DOTALL)

    # Write back
    with open(sch_file, 'w') as f:
        f.write(content)

    print(f"  Convertidas {len(labels)} etiquetas a jerárquicas")

    return labels

def add_pins_to_main_sheet(sheet_name, sheet_info, labels):
    """Agrega pines jerárquicos al sheet en el schematic principal"""
    main_sch = os.path.join(PROJ_DIR, "amper_volt_meter.kicad_sch")

    with open(main_sch, 'r') as f:
        content = f.read()

    # Find the sheet and add pins before the closing parenthesis
    sheet_uuid = sheet_info['uuid']

    # Build the pins block
    pins_block = ""
    for label in labels:
        pin_uuid = str(uuid.uuid4())
        # Adjust position relative to sheet
        pin_x = label['x']
        pin_y = label['y']
        pins_block += f"""	(hierarchical_label
		(name "{label['name']}")
		(shape bidirectional)
		(at {pin_x} {pin_y} {label['rotation']})
		(fields_autoplaced yes)
		(effects
			(font
				(size 1.27 1.27)
			)
		)
		(uuid "{pin_uuid}")
	)
"""

    # Find the sheet instance and add pins
    # We need to find the specific sheet and add pins inside it
    pattern = rf'(\(sheet\s.*?\(uuid\s+"{sheet_uuid}"\).*?\(instances.*?\n\t\)\n\t\))'

    def add_pins_to_sheet(match):
        sheet_content = match.group(1)
        # Add pins before the last closing parenthesis of the sheet
        insert_pos = sheet_content.rfind(')')
        return sheet_content[:insert_pos] + pins_block + sheet_content[insert_pos:]

    content = re.sub(pattern, add_pins_to_sheet, content, flags=re.DOTALL)

    with open(main_sch, 'w') as f:
        f.write(content)

    print(f"  Agregados {len(labels)} pines al schematic principal")

def main():
    print("=== Conversión de Etiquetas Globales a Pines Jerárquicos ===\n")

    sheets = get_sheet_uuids()
    print(f"Encontrados {len(sheets)} sheets:\n")

    for sheet_name, sheet_info in sheets.items():
        print(f"Sheet: {sheet_name}")
        print(f"  UUID: {sheet_info['uuid']}")
        print(f"  Archivo: {sheet_info['file']}")

        labels = convert_sheet(sheet_name, sheet_info)
        if labels:
            add_pins_to_main_sheet(sheet_name, sheet_info, labels)

        print()

    print("=== Conversión completada ===")

if __name__ == "__main__":
    main()
