import pyautogui
import time
import numpy as np
import math
import random
from pynput import keyboard, mouse

# ==========================================
# CONFIGURACIÓN DE VARIABLES GLOBALES
# ==========================================
COLOR_CRAB = [0, 241, 255] # Celeste
COLOR_TILE = [245, 0, 0]   # Rojos

CENTER = (0, 0)
REGION_JUEGO = (0, 0, 0, 0) 
REGION_XP = (0, 0, 0, 0) 

script_running = True
script_paused = False # Nueva variable para controlar la pausa

# ==========================================
# FUNCIONES DE CONFIGURACIÓN INICIAL
# ==========================================

def configurar_pantalla():
    """Espera 3 clics del usuario para configurar las coordenadas dinámicamente."""
    global CENTER, REGION_JUEGO, REGION_XP
    clics_capturados = []

    print("\n" + "="*50)
    print("MÓDULO DE CONFIGURACIÓN")
    print("="*50)
    print("Ahora haz 3 clics con el botón IZQUIERDO del mouse en este orden:")
    print("  1. En el CENTRO exacto de tu personaje.")
    print("  2. En la esquina INFERIOR IZQUIERDA del XP tracker.")
    print("  3. En la esquina SUPERIOR DERECHA del XP tracker.")
    print("\n[!] Escuchando clics del mouse...")

    def on_click(x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            clics_capturados.append((int(x), int(y)))
            print(f"[*] Clic {len(clics_capturados)} registrado en: ({int(x)}, {int(y)})")
            
            if len(clics_capturados) == 3:
                return False 

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # --- Cálculos Matemáticos ---
    CENTER = clics_capturados[0]

    ancho_juego = 644
    alto_juego = 528
    REGION_JUEGO = (
        CENTER[0] - (ancho_juego // 2), 
        CENTER[1] - (alto_juego // 2), 
        ancho_juego, 
        alto_juego
    )

    x1, y1 = clics_capturados[1]
    x2, y2 = clics_capturados[2]
    
    xp_left = min(x1, x2)
    xp_top = min(y1, y2)
    xp_width = abs(x2 - x1)
    xp_height = abs(y2 - y1)
    
    REGION_XP = (xp_left, xp_top, xp_width, xp_height)

    print("\n[+] ¡Configuración completada!")
    print(f"    -> Centro: {CENTER}")
    print(f"    -> Región Juego: {REGION_JUEGO}")
    print(f"    -> Región XP: {REGION_XP}\n")

# ==========================================
# FUNCIONES DE CONTROL Y VISIÓN
# ==========================================

def on_press(key):
    """Controla el Kill Switch (ESC) y la Pausa (P)."""
    global script_running, script_paused
    
    try:
        if key == keyboard.Key.esc:
            print("\n[!] Kill switch activado. Deteniendo el script de forma segura...")
            script_running = False
            return False
            
        elif key.char and key.char.lower() == 'p':
            script_paused = not script_paused # Alterna el estado de pausa
            estado = "PAUSADO" if script_paused else "REANUDADO"
            print(f"\n[!] === SCRIPT {estado} === [Presiona 'P' para cambiar, 'ESC' para salir]")
            
    except AttributeError:
        # Ignora teclas especiales que no tienen atributo .char (como Shift, Ctrl)
        pass

def human_click(x, y):
    offset_x = random.randint(-4, 4)
    offset_y = random.randint(-4, 4)
    duration = random.uniform(0.15, 0.35)
    pyautogui.moveTo(x + offset_x, y + offset_y, duration=duration, tween=pyautogui.easeOutQuad)
    time.sleep(random.uniform(0.05, 0.15))
    pyautogui.click()

def fast_move_and_verify_click(x, y, target_color):
    offset_x = random.randint(-4, 4)
    offset_y = random.randint(-4, 4)
    pyautogui.moveTo(x + offset_x, y + offset_y, duration=random.uniform(0.05, 0.10), tween=pyautogui.easeOutQuad)
    
    mx, my = pyautogui.position()
    box = (mx - 15, my - 15, 30, 30) 
    img = np.array(pyautogui.screenshot(region=box))
    
    R, G, B = target_color
    tolerancia = 15
    mask = (
        (np.abs(img[:, :, 0].astype(int) - R) <= tolerancia) &
        (np.abs(img[:, :, 1].astype(int) - G) <= tolerancia) &
        (np.abs(img[:, :, 2].astype(int) - B) <= tolerancia)
    )
    
    if np.any(mask): 
        time.sleep(random.uniform(0.01, 0.03)) 
        pyautogui.click()
        return True
    return False

def get_white_mask(region):
    img = np.array(pyautogui.screenshot(region=region))
    mask = (img[:, :, 0] > 240) & (img[:, :, 1] > 240) & (img[:, :, 2] > 240)
    return mask

def is_fighting(ultimo_estado_combate):
    print("[*] Verificando combate (analizando texto del XP tracker)...")
    mask_inicial = get_white_mask(REGION_XP)
    
    if ultimo_estado_combate:
        tiempo_espera = random.uniform(2.5, 3)
    else:
        tiempo_espera = random.uniform(1.35, 1.5)
        
    pasos = int(tiempo_espera / 0.5)
    
    for _ in range(pasos):
        if not script_running: return False
        # Si pausamos mientras verifica el combate, salimos rápido de esta función
        if script_paused: return False 
        time.sleep(0.5)
        
    mask_final = get_white_mask(REGION_XP)
    
    if not np.array_equal(mask_inicial, mask_final):
        print(f"[+] En combate (XP subiendo comprobada en {tiempo_espera:.1f}s).")
        return True
    
    print(f"[-] Fuera de combate (comprobado en {tiempo_espera:.1f}s).")
    return False

def find_target_by_color(target_color, find_furthest=False):
    img_array = np.array(pyautogui.screenshot(region=REGION_JUEGO))
    R_target, G_target, B_target = target_color
    tolerancia = 15
    mask = (
        (np.abs(img_array[:, :, 0].astype(int) - R_target) <= tolerancia) &
        (np.abs(img_array[:, :, 1].astype(int) - G_target) <= tolerancia) &
        (np.abs(img_array[:, :, 2].astype(int) - B_target) <= tolerancia)
    )

    matches = np.where(mask)
    if len(matches[0]) == 0:
        return None

    opciones_validas = []
    pesos_distancia = []

    for i in range(0, len(matches[0]), 5): 
        screen_x = matches[1][i] + REGION_JUEGO[0]
        screen_y = matches[0][i] + REGION_JUEGO[1]
        dist = math.sqrt((screen_x - CENTER[0])**2 + (screen_y - CENTER[1])**2)
        
        if find_furthest:
            opciones_validas.append((screen_x, screen_y))
            pesos_distancia.append(dist ** 3) 
        else:
            if dist > 20: 
                opciones_validas.append((screen_x, screen_y, dist))
                
    if not opciones_validas:
        return None

    if find_furthest:
        eleccion = random.choices(opciones_validas, weights=pesos_distancia, k=1)[0]
        return eleccion
    else:
        mejor_opcion = min(opciones_validas, key=lambda x: x[2])
        return (mejor_opcion[0], mejor_opcion[1])

# ==========================================
# BUCLE PRINCIPAL (MÁQUINA DE ESTADOS)
# ==========================================

def main():
    # 1. Esperar la tecla 'S' para empezar a configurar
    print("="*50)
    print("PASO 1: PREPARACIÓN")
    print("="*50)
    print("[!] Ve al juego y acomoda tu ventana de RuneScape.")
    print("[!] Cuando estés listo, presiona la tecla 'S' para habilitar los clics de configuración.")

    def wait_for_s(key):
        try:
            if key.char and key.char.lower() == 's':
                return False 
        except AttributeError:
            pass

    with keyboard.Listener(on_press=wait_for_s) as start_listener:
        start_listener.join()
        
    # 2. Ejecutar la configuración de pantalla (Los 3 clics)
    configurar_pantalla()

    # 3. Arrancar bot
    print("[+] Empezando la cacería en 3 segundos...")
    print("    (Controles: 'P' para Pausar/Reanudar | 'ESC' para Apagar)")
    time.sleep(3)
    
    # Iniciar el listener de seguridad y control
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    estado_combate = False

    while script_running:
        # Bucle de pausa: se queda aquí girando suavemente si script_paused es True
        if script_paused:
            time.sleep(0.5)
            continue

        try:
            estado_combate = is_fighting(estado_combate)
            
            # Si se pausó justo después de salir de is_fighting, vuelve al inicio del while
            if script_paused: continue 
            
            if estado_combate:
                time.sleep(random.uniform(1.0, 2.5))
                continue
            
            print("[*] Buscando Ammonite Crab...")
            crab_pos = find_target_by_color(COLOR_CRAB, find_furthest=False)
            
            if crab_pos:
                print(f"[+] Cangrejo detectado en {crab_pos}. Interceptando...")
                acierto = fast_move_and_verify_click(crab_pos[0], crab_pos[1], COLOR_CRAB)
                
                if acierto:
                    print("[+] Clic exitoso en el cangrejo.")
                    time.sleep(random.uniform(1.5, 2.0)) 
                else:
                    print("[-] El cangrejo se movió. Recalculando...")
                continue

            print("[-] No hay cangrejos. Buscando tile azul/rojo para moverse...")
            tile_pos = find_target_by_color(COLOR_TILE, find_furthest=True)
            
            if tile_pos:
                print(f"[+] Moviéndose a un tile distante para resetear aggro.")
                human_click(tile_pos[0], tile_pos[1])
                time.sleep(random.uniform(1.0, 2.0)) 
            else:
                print("[!] No se ven cangrejos ni tiles. Esperando repoblación...")
                time.sleep(random.uniform(2.0, 3.5))
                
        except Exception as e:
            print(f"Error en el ciclo principal: {e}")
            time.sleep(2)

    print("\nScript finalizado exitosamente.")

if __name__ == "__main__":
    main()