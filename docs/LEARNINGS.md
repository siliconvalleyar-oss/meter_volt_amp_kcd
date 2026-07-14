# Habilidades y Proceso de Trabajo

## 1. Organización de Librerías KiCad

### Problema
Múltiples carpetas con archivos duplicados (.kicad_mod, .kicad_sym, .step).

### Proceso
1. **Escanear directorio**: Buscar todos los archivos por extensión
2. **Identificar duplicados**: Comparar nombres de archivo
3. **Verificar contenido**: Usar `md5` para detectar archivos idénticos
4. **Crear estructura limpia**:
   - `symbols.kicad_sym` (un solo archivo con todos los símbolos)
   - `footprints.pretty/` (carpeta con footprints individuales)
   - `3dmodels/` (carpeta con modelos STEP)
5. **Mergear símbolos**: Script Python para combinar .kicad_sym únicos

---

## 2. Extracción de Footprints desde PCB

### Proceso
```bash
# 1. Extraer nombres de footprints del PCB
grep -o '(footprint "[^"]*"' archivo.kicad_pcb | sed 's/(footprint "//;s/"//' | sort -u

# 2. Verificar cuáles faltan en la librería
while read fp; do
  name=$(echo "$fp" | sed 's/.*://')
  if [ -f "footprints.pretty/$name.kicad_mod" ]; then
    echo "✅ $fp"
  else
    echo "❌ $fp (FALTA)"
  fi
done < footprints_faltantes.txt

# 3. Buscar en librerías estándar de KiCad
find /Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints -name "NombreFootprint.kicad_mod"

# 4. Copiar a la librería
cp /ruta/al/footprint.kicad_mod footprints.pretty/
```

---

## 3. Licencias

### Ubicación de licencias en macOS
```bash
# KiCad bundle
ls /Applications/KiCad/KiCad.app/Contents/Resources/Licenses/

# Solo contiene Python/LICENSE.txt (PSF License)
# NO hay licencia KiCad como archivo separado
```

### KiCad usa GPL v2+
- El binario de KiCad contiene la licencia GPL v2+ embebida
- Los proyectos y librerías creados con KiCad deben ser compatibles
- **Solución**: Crear archivo `LICENSE` manualmente con texto GPL v2+

### Crear LICENSE
```bash
# Descargar texto oficial
curl -o LICENSE https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

# O crear manualmente con el texto de gnu.org
```

---

## 4. Git Push con Token (HTTPS)

### Configuración
```bash
# Verificar usuario git local
git config user.name
git config user.email

# Verificar remote
git remote -v
```

### Proceso de Push
```bash
# 1. Temporalmente configurar remote con token
git remote set-url origin https://USUARIO:TOKEN@github.com/USUARIO/REPOSITORIO.git

# 2. Push
git push -u origin main

# 3. IMPORTANTE: Limpiar remote (quitar token)
git remote set-url origin https://github.com/USUARIO/REPOSITORIO.git
```

### Seguridad
- **NUNCA** commitear tokens en el repositorio
- **NUNCA** mostrar tokens en logs o pantallas
- **SIEMPRE** limpiar la URL después del push
- El token se almacena en la config global de git (no en el repositorio)

---

## 5. Verificación de Contenido

### Contar archivos
```bash
# Footprints
ls footprints.pretty/*.kicad_mod | wc -l

# Símbolos (entradas principales)
grep -c '(symbol "' symbols.kicad_sym

# Modelos 3D
ls 3dmodels/*.step | wc -l
```

### Detectar duplicados
```bash
# Por nombre
find . -name "*.kicad_mod" -exec basename {} \; | sort | uniq -c | sort -rn

# Por contenido (hash MD5)
find . -name "*.kicad_mod" -exec md5 -r {} \; | awk '{print $1}' | sort | uniq -d
```

---

## 6. Estructura de Repositorio KiCad

```
repositorio/
├── symbols.kicad_sym      # Todos los símbolos en un archivo
├── footprints.pretty/      # Carpeta con footprints (.kicad_mod)
├── 3dmodels/              # Modelos STEP (.step)
├── LICENSE                # GPL v2+ (obligatorio)
├── README.md              # Documentación
└── .gitignore             # Excluir: *.zip, *.bak, .DS_Store, etc.
```

---

## 7. Script de Mergear Símbolos

```python
#!/usr/bin/env python3
import os
import re

def merge_symbols(source_dirs, output_file):
    """Combina múltiples .kicad_sym en uno solo"""
    unique_symbols = {}
    
    for source_dir in source_dirs:
        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                if filename.endswith('.kicad_sym'):
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r') as f:
                        content = f.read()
                        symbols = re.findall(
                            r'\(symbol\s+"[^"]+".*?\n\s+\)\s*\)',
                            content, re.DOTALL
                        )
                        for symbol in symbols:
                            name = re.search(r'\(symbol\s+"([^"]+)"', symbol)
                            if name and name.group(1) not in unique_symbols:
                                unique_symbols[name.group(1)] = symbol
    
    with open(output_file, 'w') as f:
        f.write('(kicad_symbol_lib (version 20211014) (generator custom)\n')
        for name, symbol in sorted(unique_symbols.items()):
            f.write('  ' + symbol + '\n')
        f.write(')\n')
    
    return len(unique_symbols)
```

---

## 8. Comandos Útiles de KiCad

```bash
# Buscar footprints en KiCad
find /Applications/KiCad -name "*.pretty" -type d

# Buscar un footprint específico
find /Applications/KiCad -name "Nombre.kicad_mod" -type f

# Verificar estructura de archivo .kicad_sym
head -20 archivo.kicad_sym
```

---

## 9. Gitignore para KiCad

```gitignore
# Archivos KiCad
*.kicad_pcb-bak
*.kicad_sch-bak
fp-info-cache

# ZIP (no subir)
*.zip

# Temporales
*.tmp
*.bak
*~

# macOS
.DS_Store

# Python
__pycache__/
*.pyc
```

---

## 10. Guía Completa: Pines Jerárquicos en Sheet Symbols

### Conceptos Clave

Un **sheet symbol** en KiCad es el rectángulo que aparece en el schematic padre (root) y representa un sub-schematic (child). Los **pins** son las conexiones que permiten pasar señales entre el padre y el hijo.

**Anatomía de un pin:**
```
(pin "NOMBRE" input
    (at X Y ROT)        ← Punto de conexión (donde se conectan los wires)
    (uuid "...")
    (effects ...)
)
```

### Regla #1: SIEMPRE offset 2.54mm FUERA del rectángulo

El `at` del pin es el **punto de conexión** (la punta). KiCad dibuja automáticamente un "stub" desde el borde del rectángulo hasta este punto.

```
RECTÁNGULO          STUB        PUNTO DE CONEXIÓN
┌──────────┐      ────────→        •  ← (at X Y)
│          │
└──────────┘
```

**Si el punto está EN el borde = zig-zag defectuoso**
**Si el punto está FUERA del borde = stub correcto**

### Fórmulas

```python
PIN_LEN = 2.54  # mm, offset estándar

# Pines IZQUIERDOS (rotación 180°)
at_x = sheet_x - PIN_LEN
at_y = sheet_y + margin + (index + 1) * SPACING

# Pines DERECHOS (rotación 0°)
at_x = sheet_x + sheet_width + PIN_LEN
at_y = sheet_y + margin + (index + 1) * SPACING
```

### Espaciado entre pines

- **Mínimo recomendado**: 2.54mm entre pines
- **Espaciado estándar**: 2.54mm (100 mil)
- **Para sheets grandes**: 2.54mm funciona bien con hasta ~80 pines

```python
SPACING = 2.54  # mm entre cada pin

# Calcular altura del sheet
needed_height = num_pins * SPACING + 2 * MARGIN
sheet_height = max(needed_height, 30.0)  # mínimo 30mm
```

### Ejemplo Completo: Sheet con 6 pines

```python
import uuid as uuid_mod

# Datos del sheet
sheet_x = 100.0
sheet_y = 50.0
sheet_w = 55.0
sheet_h = 40.0
pin_len = 2.54
margin = 5.0
spacing = 2.54

# Pines del sub-schematic (ordenados por puerto)
left_labels = ['AN8', 'AN9', 'RA0']   # 3 pines
right_labels = ['RD2', 'RD3', 'RD4']  # 3 pines

# Generar pines izquierdos
for i, name in enumerate(left_labels):
    y = sheet_y + margin + (i + 1) * spacing
    pin = f'''		(pin "{name}" input
			(at {sheet_x - pin_len} {y:.2f} 180)
			(uuid "{str(uuid_mod.uuid4())}")
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)'''

# Generar pines derechos
for i, name in enumerate(right_labels):
    y = sheet_y + margin + (i + 1) * spacing
    pin = f'''		(pin "{name}" input
			(at {sheet_x + sheet_w + pin_len} {y:.2f} 0)
			(uuid "{str(uuid_mod.uuid4())}")
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify right)
			)
		)'''
```

### Visualización del resultado

```
         PIN_IZQ              RECTÁNGULO              PIN_DER
            •───────────────┌──────────┐───────────────• AN8
            •───────────────│          │───────────────• AN9
            •───────────────│  CHILD   │───────────────• RD2
                             │          │
                             └──────────┘
    X = sheet_x - 2.54                          X = sheet_x + width + 2.54
```

### Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| Zig-zag verde | `at` en el borde del rectángulo | Mover `at` 2.54mm fuera |
| Pines superpuestos | Espaciado < 2.54mm | Usar spacing = 2.54 |
| Pins fuera de vista | Sheet muy pequeño | Calcular `sheet_h` según num_pins |
| Pins mezclados entre sheets | Búsqueda regex incorrecta | Usar `instances` como límite |

### Script de Verificación

```python
import re

def verify_sheet_pins(filepath, sheet_uuid):
    with open(filepath) as f:
        content = f.read()
    
    idx = content.find(f'uuid "{sheet_uuid}"')
    sheet_start = content.rfind('(sheet', 0, idx)
    instances_idx = content.find('(instances', idx)
    sheet_section = content[sheet_start:instances_idx]
    
    # Encontrar posición del sheet
    at_match = re.search(r'\(at ([\d.]+) ([\d.]+)\)', content[sheet_start:idx])
    sheet_x = float(at_match.group(1))
    
    size_match = re.search(r'\(size ([\d.]+) ([\d.]+)\)', content[sheet_start:idx])
    sheet_w = float(size_match.group(1))
    
    # Verificar pins
    left_x_correct = sheet_x - 2.54
    right_x_correct = sheet_x + sheet_w + 2.54
    
    for m in re.finditer(r'\(pin "([^"]+)" input\s*\n\s*\(at ([\d.]+) ([\d.]+) (\d+)\)', sheet_section):
        name, x, y, rot = m.group(1), float(m.group(2)), float(m.group(3)), int(m.group(4))
        if rot == 180 and abs(x - left_x_correct) > 0.1:
            print(f'WARNING: {name} left pin at wrong X: {x} (expected {left_x_correct})')
        elif rot == 0 and abs(x - right_x_correct) > 0.1:
            print(f'WARNING: {name} right pin at wrong X: {x} (expected {right_x_correct})')
    
    print('Verification complete')
```

### Resumen de Reglas

1. **Siempre** offset 2.54mm fuera del rectángulo
2. **Siempre** espaciado de 2.54mm entre pins
3. **Calcular** altura del sheet según número de pins
4. **Ordenar** pins por puerto (RA, RB, RC, RD, etc.)
5. **Verificar** que todos los pins están en la posición correcta

---

## 11. Flujo de Trabajo Completo

1. **Explorar**: Encontrar todos los archivos en el directorio
2. **Deduplicar**: Identificar y eliminar duplicados
3. **Organizar**: Crear estructura limpia (symbols, footprints, 3d)
4. **Mergear**: Combinar símbolos en un solo archivo
5. **Verificar**: Contar archivos, detectar faltantes
6. **Documentar**: Actualizar README con contenido real
7. **Licenciar**: Agregar GPL v2+ (requerido por KiCad)
8. **Git init**: Inicializar repositorio
9. **Commit**: Guardar cambios
10. **Push**: Subir a GitHub (con token temporal)
11. **Limpiar**: Remover token del remote
