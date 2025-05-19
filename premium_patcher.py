def find_and_modify_isPremiumFeatureAvailable(root_directory):
    """
    Encuentra y modifica todos los métodos isPremiumFeatureAvailable en el APK descompilado
    para que devuelvan siempre true.
    """
    import os
    import re
    
    # Colores para mensajes en la terminal
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    NC = "\033[0m"  # No Color
    
    methods_found = 0
    files_modified = 0
    
    # Patrones para buscar el método isPremiumFeatureAvailable
    method_patterns = [
        r"\.method (?:private|public|protected)(?: final)? isPremiumFeatureAvailable\(I\)Z",  # Método declaración
        r"Lorg/telegram/.*->isPremiumFeatureAvailable\(I\)Z"  # Referencias al método
    ]
    
    # Patrón para encontrar archivos smali relevantes
    for root, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".smali"):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    print(f"{YELLOW}WARN: {NC}Error al leer {file_path}: {e}")
                    continue
                
                # Buscar cualquier referencia al método
                method_match = False
                for pattern in method_patterns:
                    if re.search(pattern, content):
                        method_match = True
                        break
                
                if not method_match:
                    continue
                
                print(f"{GREEN}INFO: {NC}Encontrado método isPremiumFeatureAvailable en {file_path}")
                methods_found += 1
                
                # Modificar el archivo
                modified = False
                new_lines = []
                in_method = False
                
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    # Detectar inicio del método
                    for pattern in method_patterns[:1]:  # Solo usar el primer patrón para la declaración del método
                        if re.search(pattern, line):
                            in_method = True
                            new_lines.append(line)
                            print(f"{GREEN}INFO: {NC}Encontrada declaración del método en línea {i+1}")
                            break
                    else:
                        # Si no es el inicio del método, añadir la línea como está
                        if not in_method:
                            new_lines.append(line)
                            continue
                    
                    # Dentro del método
                    if in_method:
                        # Modificar la línea que establece el valor de retorno a false (0x0)
                        if "const/4" in line and "0x0" in line:
                            new_lines.append(line.replace("const/4 v0, 0x0", "const/4 v0, 0x1").replace("const/4 v1, 0x0", "const/4 v1, 0x1"))
                            modified = True
                            print(f"{GREEN}INFO: {NC}Modificada línea {i+1}: {line.strip()} -> const/4 vX, 0x1")
                        else:
                            new_lines.append(line)
                        
                        # Detectar fin del método
                        if ".end method" in line:
                            in_method = False
                
                # Guardar cambios si se modificó algo
                if modified:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    files_modified += 1
                    print(f"{GREEN}INFO: {NC}Archivo {file_path} modificado con éxito")
    
    # Búsqueda adicional para modificar invocaciones directas
    for root, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".smali"):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    continue
                
                # Buscar invoke-direct o invoke-virtual al método
                if "invoke-" in content and "isPremiumFeatureAvailable(I)Z" in content:
                    # Buscar el patrón de uso del resultado (normalmente if-eqz o if-nez después de la invocación)
                    lines = content.split('\n')
                    modified = False
                    new_lines = []
                    
                    i = 0
                    while i < len(lines):
                        line = lines[i]
                        new_lines.append(line)
                        
                        # Si encuentra una invocación a isPremiumFeatureAvailable
                        if "invoke-" in line and "isPremiumFeatureAvailable(I)Z" in line:
                            print(f"{GREEN}INFO: {NC}Encontrada invocación a isPremiumFeatureAvailable en {file_path}")
                            
                            # Obtener el registro de resultado
                            result_reg_match = re.search(r"move-result[^ ]* (v\d+)", lines[i+1] if i+1 < len(lines) else "")
                            if result_reg_match:
                                result_reg = result_reg_match.group(1)
                                
                                # Reemplazar move-result con const/4 v{reg}, 0x1
                                if i+1 < len(lines):
                                    new_lines.append(f"    const/4 {result_reg}, 0x1")
                                    i += 1  # Saltar la línea original de move-result
                                    modified = True
                                    print(f"{GREEN}INFO: {NC}Reemplazada línea move-result por const/4 {result_reg}, 0x1")
                        
                        i += 1
                    
                    # Guardar cambios si se modificó algo
                    if modified:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write("\n".join(new_lines))
                        files_modified += 1
                        print(f"{GREEN}INFO: {NC}Archivo {file_path} modificado con éxito (invocación)")
    
    if methods_found > 0:
        print(f"{GREEN}INFO: {NC}Se encontraron {methods_found} métodos isPremiumFeatureAvailable y se modificaron {files_modified} archivos.")
        return True
    else:
        print(f"{YELLOW}WARN: {NC}No se encontró ningún método isPremiumFeatureAvailable en los archivos smali.")
        return False


# Esta función debe ser añadida al script principal y reemplazar o complementar la función existente
def patch_premium_features(root_directory):
    """Parche todas las características premium."""
    print(f"\n{GREEN}[+] {NC}Parcheando características premium...")
    
    # Llamar a la función mejorada para buscar y modificar isPremiumFeatureAvailable
    premium_patched = find_and_modify_isPremiumFeatureAvailable(root_directory)
    
    # Aquí pueden agregarse más parches relacionados con funciones premium
    
    return premium_patched
