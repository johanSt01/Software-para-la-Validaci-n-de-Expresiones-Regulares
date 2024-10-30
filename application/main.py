import re
import tkinter as tk
from tkinter import messagebox

#iniciar la ejecucio del codigo
# Función para ejecutar el código principal de validación
def ejecutarCodigo():
    expresion_regular = entrada_expresion.get()  # Obtiene la expresión regular de la interfaz
    cadena = entrada_cadena.get()  # Obtiene la cadena de la interfaz

    resultado = analisisLexico(expresion_regular)  # Análisis léxico

    if resultado:
        print('Análisis léxico cumplido')
        resultado = analisisSintactico(expresion_regular)  # Análisis sintáctico

        if resultado:
            print('Análisis sintáctico cumplido')
            pertenece = pertenece_a_expresion(expresion_regular, cadena)
            if pertenece:
                messagebox.showinfo("Resultado", "La cadena pertenece a la expresión regular.")
            else:
                messagebox.showinfo("Resultado", "La cadena NO pertenece a la expresión regular.")
        else:
            messagebox.showerror("Error", "Análisis sintáctico fallido.")
    else:
        messagebox.showerror("Error", "Análisis léxico fallido.")




#hacer el analisis lexico a la expresion
def analisisLexico(expresion_regular: str):
    """
    Realizar el análisis léxico a la expresión regular, asegurándose de que todos
    los elementos ingresados sean procesables.
    
    Parametros:
    - expresion_regular (str): La expresión regular a analizar.
    
    Retorna:
    - bool: True si todos los tokens son válidos, False en caso contrario.
    """
    # Conjunto de tokens válidos
    operadores_validos = {'*', '+', '{', '}', '|', '.', '@', ',',':',';','-'}
    
    # Tokeniza cada carácter individual de la expresión
    tokens = list(expresion_regular)
    
    for token in tokens:
        # Se verifica si el token es un número, una letra o un operador válido
        if not (token.isalnum() or token in operadores_validos):
            print(f"Token inválido encontrado: '{token}'")
            return False  
    
    print("Todos los tokens son válidos.")
    return True  # Retorna True si todos los tokens son válidos


#analizar que el orden de la expresion tenga el orden correcto
def analisisSintactico(expresion_regular: str) -> bool:
    """
    Realizar el análisis sintáctico a la expresión, asegurando que sigue una sintaxis
    establecida mediante el uso de un autómata con las reglas especificadas, incluyendo
    la validación de rangos con el carácter '-' dentro de llaves y permitiendo operadores de cerradura dentro de ellas.
    
    Parametros:
    - expresion_regular (str): La expresión regular a analizar.
    
    Retorna:
    - bool: True si la sintaxis es correcta, False en caso contrario.
    """
    # Estados iniciales y configuraciones
    estado = "INICIO"
    balance_llaves = 0
    i = 0
    longitud = len(expresion_regular)
    
    while i < longitud:
        token = expresion_regular[i]
        
        # Estado de inicio: espera una letra, número, o un operador válido (excluye *, +, |, {, })
        if estado == "INICIO":
            if token.isalnum():
                estado = "OPERANDO"
            elif token == '{':
                balance_llaves += 1
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: carácter inesperado '{token}' en el inicio.")
                return False

        # Estado OPERANDO: tras una letra, número o conjunto, puede seguir un operador, llave o un rango con '-'.
        elif estado == "OPERANDO":
            if token in {'*', '+'}:
                estado = "OPERADOR_UNARIO"
            elif token == '|':
                estado = "OPERADOR_BINARIO"
            elif token == '{':
                balance_llaves += 1
                estado = "EN_LLAVE"
            elif token == '-':
                print("Error sintáctico: el guion '-' solo puede utilizarse dentro de llaves para definir un rango.")
                return False
            elif token == '}':
                print("Error sintáctico: llave de cierre sin apertura.")
                return False

        # Estado EN_LLAVE: permite letras, números, operadores de unión, cerraduras y rangos.
        elif estado == "EN_LLAVE":
            if token == '}':
                balance_llaves -= 1
                estado = "OPERANDO"
            elif token == '|':
                # Verifica que `|` esté entre caracteres alfanuméricos
                if i == 0 or i == longitud - 1 or not (expresion_regular[i-1].isalnum() and expresion_regular[i+1].isalnum()):
                    print("Error sintáctico: el operador '|' debe estar entre caracteres alfanuméricos dentro de llaves.")
                    return False
            elif token == '-':
                # Validación de rango dentro de llaves: el '-' debe estar rodeado de caracteres alfanuméricos.
                if i == 0 or i == longitud - 1 or not (expresion_regular[i-1].isalnum() and expresion_regular[i+1].isalnum()):
                    print("Error sintáctico: el guion '-' debe definir un rango entre dos caracteres dentro de llaves.")
                    return False
                estado = "RANGO"
            elif token in {'*', '+'}:
                # Permite `*` o `+` solo si sigue a un alfanumérico válido dentro de `{}` como una cerradura
                if i == 0 or not expresion_regular[i-1].isalnum():
                    print(f"Error sintáctico: operador '{token}' en posición inválida dentro de llaves.")
                    return False
                # Se considera parte de la cerradura y no cambia de estado
            elif token.isalnum() or token in {'.', '@', ',', '(', ')'}:
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: carácter '{token}' inesperado dentro de llaves.")
                return False

        # Estado RANGO: tras un '-', debe aparecer un carácter alfanumérico para cerrar el rango.
        elif estado == "RANGO":
            if token.isalnum():
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: se esperaba un carácter alfanumérico para completar el rango tras '-'.")
                return False

        # Estado OPERADOR_UNARIO: después de * o +, puede continuar con otro operador o llaves
        elif estado == "OPERADOR_UNARIO":
            if token == '|':
                estado = "OPERADOR_BINARIO"
            elif token.isalnum():
                estado = "OPERANDO"
            elif token == '{':
                balance_llaves += 1
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: carácter '{token}' inesperado tras operador unario.")
                return False

        # Estado OPERADOR_BINARIO: espera un operando después de un operador binario
        elif estado == "OPERADOR_BINARIO":
            if token.isalnum():
                estado = "OPERANDO"
            elif token == '{':
                balance_llaves += 1
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: carácter '{token}' inválido tras operador binario.")
                return False

        i += 1

    # Al finalizar, validar que las llaves estén balanceadas
    if balance_llaves != 0:
        print("Error sintáctico: llaves desbalanceadas.")
        return False

    print("La sintaxis es correcta.")
    return True





#validar si una cadena cumple una expresion regular
def pertenece_a_expresion(expresion_regular: str, cadena: str) -> bool:
    """
    Valida si una cadena pertenece a la expresión regular dada, considerando
    cerradura estrella (*), cerradura positiva (+) y unión (|), con concatenación.
    
    Parametros:
    - expresion_regular (str): La expresión regular en formato personalizado.
    - cadena (str): La cadena que se desea validar contra la expresión.
    
    Retorna:
    - bool: True si la cadena pertenece a la expresión regular, False en caso contrario.
    """
    # Se pasa la expresión personalizada a una expresión compatible con Python
    regex = convertir_a_regex(expresion_regular)
    
    # Se verifica si la cadena completa coincide con la expresión regular
    resultado = re.fullmatch(regex, cadena)
    
    # Si hay coincidencia, la cadena pertenece; si no, no pertenece
    if resultado:
        print(f"La cadena '{cadena}' pertenece a la expresión regular '{expresion_regular}'.")
        return True
    else:
        print(f"La cadena '{cadena}' NO pertenece a la expresión regular '{expresion_regular}'.")
        return False



#convertir la expresion personalidada a una expresion manejada por python
def convertir_a_regex(expresion_regular: str) -> str:
    """
    Convierte una expresión regular en formato personalizado a una expresión regular
    estándar de Python.
    
    Parametros:
    - expresion_regular (str): La expresión regular en formato personalizado.
    
    Retorna:
    - str: La expresión regular convertida para ser utilizada en re.fullmatch().
    """
    # Cadena donde se irá construyendo la expresión compatible con Python
    regex = ""
    i = 0
    longitud = len(expresion_regular)
    
    while i < longitud:
        token = expresion_regular[i]
        
        if token == '*':
            # Cerradura estrella, se agrega tal cual
            regex += '*'
        elif token == '+':
            # Cerradura positiva, se agrega tal cual
            regex += '+'
        elif token == '|':
            # Unión, se agrega tal cual
            regex += '|'
        elif token == '{':
            # Si se encuentra una llave abierta, se captura todo el conjunto dentro de ella
            conjunto = ""
            i += 1  # Avanza para saltar la llave abierta '{'
            while i < longitud and expresion_regular[i] != '}':
                conjunto += expresion_regular[i]
                i += 1
            
            # Validamos y convertimos el contenido del conjunto
            if '-' in conjunto:
                # Detectar si es un rango en formato "a-z" o "0-9"
                partes = conjunto.split('-')
                if len(partes) == 2 and partes[0].isalnum() and partes[1].isalnum():
                    # Si es un rango válido, construimos el rango en regex
                    regex += f"[{partes[0]}-{partes[1]}]"
                else:
                    print(f"Error de sintaxis en el rango: {conjunto}")
                    return ""
            else:
                # Si no es un rango, simplemente agrupa el conjunto
                regex += f"(?:{conjunto})"
        elif token.isalnum() or token in {'.', '@', ',', '(', ')'}:
            # Los operandos válidos se agregan directamente
            regex += token
        else:
            # Si hay un carácter no reconocido, se retorna una cadena vacía
            print(f"Carácter no reconocido en la expresión: {token}")
            return ""
        
        i += 1
    
    return regex





#leer una expresion regular
def leerExpresionRegular():
    """
        Solitiar al usuario una expresion regular para trabajar
    """
    return str(input('hola, por favor digita la exprecion regular: '))



# Configuración de la interfaz gráfica
ventana = tk.Tk()
ventana.title("Validador de Expresiones Regulares")
ventana.geometry("400x200")

# Campo de texto para la expresión regular
tk.Label(ventana, text="Expresión Regular:").pack()
entrada_expresion = tk.Entry(ventana, width=50)
entrada_expresion.pack()

# Campo de texto para la cadena a validar
tk.Label(ventana, text="Ingrese una cadena a validar:").pack()
entrada_cadena = tk.Entry(ventana, width=50)
entrada_cadena.pack()

# Botón para iniciar la validación
boton_validar = tk.Button(ventana, text="Validar", command=ejecutarCodigo)
boton_validar.pack()

# Iniciar la interfaz gráfica
ventana.mainloop()



#iniciar programa
# if __name__ == '__main__':
#     ejecutarCodigo()