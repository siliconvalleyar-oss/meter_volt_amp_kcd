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

## 10. Flujo de Trabajo Completo

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
