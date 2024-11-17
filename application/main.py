import tkinter as tk
from tkinter import messagebox
import re


# Función para ejecutar el código principal de validación
def ejecutarCodigo():
    expresion_regular = entrada_expresion.get()  # Obtiene la expresión regular de la interfaz
    try:
        cantidad_cadenas = int(entrada_cant_cadenas.get())  # Obtiene la cantidad de cadenas a validar
    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese un número válido para la cantidad de cadenas.")
        return

    # Recopilar las cadenas ingresadas por el usuario
    cadenas = []
    for i in range(cantidad_cadenas):
        cadena = entradas_cadenas[i].get()  # Obtiene cada cadena
        cadenas.append(cadena)

    # Ejecutar validación para cada cadena
    resultado = analisisLexico(expresion_regular)  # Análisis léxico
    if resultado:
        print('Análisis léxico cumplido')
        resultado = analisisSintactico(expresion_regular)  # Análisis sintáctico

        if resultado:
            print('Análisis sintáctico cumplido')
            for cadena in cadenas:
                pertenece = pertenece_a_expresion(expresion_regular, cadena)
                if pertenece:
                    messagebox.showinfo("Resultado", f"La cadena '{cadena}' pertenece a la expresión regular.")
                else:
                    messagebox.showinfo("Resultado", f"La cadena '{cadena}' NO pertenece a la expresión regular.")
        else:
            messagebox.showerror("Error", "Análisis sintáctico fallido.")
    else:
        messagebox.showerror("Error", "Análisis léxico fallido.")


# Hacer el análisis léxico a la expresión
def analisisLexico(expresion_regular: str):
    """
        Realizar el análisis léxico a la expresión regular, asegurándose de que todos
        los elementos ingresados sean procesables.

        Parametros:
        - expresion_regular (str): La expresión regular a analizar.

        Retorna:
        - bool: True si todos los tokens son válidos, False en caso contrario.
        """
    operadores_validos = {'*', '+', '{', '}', '|', '.', '@', ',', ':', ';', '-'}

    tokens = list(expresion_regular)

    for token in tokens:
        if not (token.isalnum() or token in operadores_validos):
            print(f"Token inválido encontrado: '{token}'")
            return False

    print("Todos los tokens son válidos.")
    return True


# Analizar el orden sintáctico de la expresión
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
    estado = "INICIO"
    balance_llaves = 0
    i = 0
    longitud = len(expresion_regular)

    while i < longitud:
        token = expresion_regular[i]

        if estado == "INICIO":
            if token.isalnum():
                estado = "OPERANDO"
            elif token == '{':
                balance_llaves += 1
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: carácter inesperado '{token}' en el inicio.")
                return False

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

        elif estado == "EN_LLAVE":
            if token == '}':
                balance_llaves -= 1
                estado = "OPERANDO"
            elif token == '|':
                if i == 0 or i == longitud - 1 or not (
                        expresion_regular[i - 1].isalnum() and expresion_regular[i + 1].isalnum()):
                    print(
                        "Error sintáctico: el operador '|' debe estar entre caracteres alfanuméricos dentro de llaves.")
                    return False
            elif token == '-':
                if i == 0 or i == longitud - 1 or not (
                        expresion_regular[i - 1].isalnum() and expresion_regular[i + 1].isalnum()):
                    print("Error sintáctico: el guion '-' debe definir un rango entre dos caracteres dentro de llaves.")
                    return False
                estado = "RANGO"
            elif token in {'*', '+'}:
                if i == 0 or not expresion_regular[i - 1].isalnum():
                    print(f"Error sintáctico: operador '{token}' en posición inválida dentro de llaves.")
                    return False
            elif token.isalnum() or token in {'.', '@', ',', '(', ')'}:
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: carácter '{token}' inesperado dentro de llaves.")
                return False

        elif estado == "RANGO":
            if token.isalnum():
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: se esperaba un carácter alfanumérico para completar el rango tras '-'.")
                return False

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

    if balance_llaves != 0:
        print("Error sintáctico: llaves desbalanceadas.")
        return False

    print("La sintaxis es correcta.")
    return True


# Validar si una cadena cumple con la expresión regular
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
    regex = convertir_a_regex(expresion_regular)

    resultado = re.fullmatch(regex, cadena)

    if resultado:
        print(f"La cadena '{cadena}' pertenece a la expresión regular '{expresion_regular}'.")
        return True
    else:
        print(f"La cadena '{cadena}' NO pertenece a la expresión regular '{expresion_regular}'.")
        return False


# Convertir la expresión personalizada a una expresión manejada por Python
def convertir_a_regex(expresion_regular: str) -> str:
    """
        Convierte una expresión regular en formato personalizado a una expresión regular
        estándar de Python.

        Parametros:
        - expresion_regular (str): La expresión regular en formato personalizado.

        Retorna:
        - str: La expresión regular convertida para ser utilizada en re.fullmatch().
        """
    regex = ""
    i = 0
    longitud = len(expresion_regular)

    while i < longitud:
        token = expresion_regular[i]

        if token == '*':
            regex += '*'
        elif token == '+':
            regex += '+'
        elif token == '|':
            regex += '|'
        elif token == '{':
            conjunto = ""
            i += 1
            while i < longitud and expresion_regular[i] != '}':
                conjunto += expresion_regular[i]
                i += 1

            if '-' in conjunto:
                partes = conjunto.split('-')
                if len(partes) == 2 and partes[0].isalnum() and partes[1].isalnum():
                    regex += f"[{partes[0]}-{partes[1]}]"
                else:
                    print(f"Error de sintaxis en el rango: {conjunto}")
                    return ""
            else:
                regex += f"(?:{conjunto})"
        elif token.isalnum() or token in {'.', '@', ',', '(', ')'}:
            regex += token
        else:
            print(f"Carácter no reconocido en la expresión: {token}")
            return ""

        i += 1

    return regex


# Leer la cantidad de cadenas
def leerCantidadCadenas():
    """
    Solicita al usuario la cantidad de cadenas que desea validar.
    """
    try:
        cantidad = int(input("Por favor ingresa la cantidad de cadenas a validar: "))
        return cantidad
    except ValueError:
        print("Por favor ingrese un número válido para la cantidad de cadenas.")
        return 0


# Configuración de la interfaz gráfica
import tkinter as tk
from tkinter import messagebox
import re


# Función para ejecutar el código principal de validación
def ejecutarCodigo():
    expresion_regular = entrada_expresion.get()  # Obtiene la expresión regular de la interfaz
    try:
        cantidad_cadenas = int(entrada_cant_cadenas.get())  # Obtiene la cantidad de cadenas a validar
    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese un número válido para la cantidad de cadenas.")
        return

    # Recopilar las cadenas ingresadas por el usuario
    cadenas = []
    for i in range(cantidad_cadenas):
        cadena = entradas_cadenas[i].get()  # Obtiene cada cadena
        cadenas.append(cadena)

    # Ejecutar validación para cada cadena
    resultado = analisisLexico(expresion_regular)  # Análisis léxico
    if resultado:
        print('Análisis léxico cumplido')
        resultado = analisisSintactico(expresion_regular)  # Análisis sintáctico

        if resultado:
            print('Análisis sintáctico cumplido')
            for cadena in cadenas:
                pertenece = pertenece_a_expresion(expresion_regular, cadena)
                if pertenece:
                    messagebox.showinfo("Resultado", f"La cadena '{cadena}' pertenece a la expresión regular.")
                else:
                    messagebox.showinfo("Resultado", f"La cadena '{cadena}' NO pertenece a la expresión regular.")
        else:
            messagebox.showerror("Error", "Análisis sintáctico fallido.")
    else:
        messagebox.showerror("Error", "Análisis léxico fallido.")


# Hacer el análisis léxico a la expresión
def analisisLexico(expresion_regular: str):
    """
    Realiza el análisis léxico a la expresión regular.
    """
    operadores_validos = {'*', '+', '{', '}', '|', '.', '@', ',', ':', ';', '-'}

    tokens = list(expresion_regular)

    for token in tokens:
        if not (token.isalnum() or token in operadores_validos):
            print(f"Token inválido encontrado: '{token}'")
            return False

    print("Todos los tokens son válidos.")
    return True


# Analizar el orden sintáctico de la expresión
def analisisSintactico(expresion_regular: str) -> bool:
    """
    Realiza el análisis sintáctico de la expresión.
    """
    estado = "INICIO"
    balance_llaves = 0
    i = 0
    longitud = len(expresion_regular)

    while i < longitud:
        token = expresion_regular[i]

        if estado == "INICIO":
            if token.isalnum():
                estado = "OPERANDO"
            elif token == '{':
                balance_llaves += 1
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: carácter inesperado '{token}' en el inicio.")
                return False

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

        elif estado == "EN_LLAVE":
            if token == '}':
                balance_llaves -= 1
                estado = "OPERANDO"
            elif token == '|':
                if i == 0 or i == longitud - 1 or not (
                        expresion_regular[i - 1].isalnum() and expresion_regular[i + 1].isalnum()):
                    print(
                        "Error sintáctico: el operador '|' debe estar entre caracteres alfanuméricos dentro de llaves.")
                    return False
            elif token == '-':
                if i == 0 or i == longitud - 1 or not (
                        expresion_regular[i - 1].isalnum() and expresion_regular[i + 1].isalnum()):
                    print("Error sintáctico: el guion '-' debe definir un rango entre dos caracteres dentro de llaves.")
                    return False
                estado = "RANGO"
            elif token in {'*', '+'}:
                if i == 0 or not expresion_regular[i - 1].isalnum():
                    print(f"Error sintáctico: operador '{token}' en posición inválida dentro de llaves.")
                    return False
            elif token.isalnum() or token in {'.', '@', ',', '(', ')'}:
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: carácter '{token}' inesperado dentro de llaves.")
                return False

        elif estado == "RANGO":
            if token.isalnum():
                estado = "EN_LLAVE"
            else:
                print(f"Error sintáctico: se esperaba un carácter alfanumérico para completar el rango tras '-'.")
                return False

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

    if balance_llaves != 0:
        print("Error sintáctico: llaves desbalanceadas.")
        return False

    print("La sintaxis es correcta.")
    return True


# Validar si una cadena cumple con la expresión regular
def pertenece_a_expresion(expresion_regular: str, cadena: str) -> bool:
    """
    Valida si una cadena pertenece a la expresión regular dada.
    """
    regex = convertir_a_regex(expresion_regular)

    resultado = re.fullmatch(regex, cadena)

    if resultado:
        print(f"La cadena '{cadena}' pertenece a la expresión regular '{expresion_regular}'.")
        return True
    else:
        print(f"La cadena '{cadena}' NO pertenece a la expresión regular '{expresion_regular}'.")
        return False


# Convertir la expresión personalizada a una expresión manejada por Python
def convertir_a_regex(expresion_regular: str) -> str:
    """
    Convierte una expresión regular personalizada a una expresión regular de Python.
    """
    regex = ""
    i = 0
    longitud = len(expresion_regular)

    while i < longitud:
        token = expresion_regular[i]

        if token == '*':
            regex += '*'
        elif token == '+':
            regex += '+'
        elif token == '|':
            regex += '|'
        elif token == '{':
            conjunto = ""
            i += 1
            while i < longitud and expresion_regular[i] != '}':
                conjunto += expresion_regular[i]
                i += 1

            if '-' in conjunto:
                partes = conjunto.split('-')
                if len(partes) == 2 and partes[0].isalnum() and partes[1].isalnum():
                    regex += f"[{partes[0]}-{partes[1]}]"
                else:
                    print(f"Error de sintaxis en el rango: {conjunto}")
                    return ""
            else:
                regex += f"(?:{conjunto})"
        elif token.isalnum() or token in {'.', '@', ',', '(', ')'}:
            regex += token
        else:
            print(f"Carácter no reconocido en la expresión: {token}")
            return ""

        i += 1

    return regex


# Leer la cantidad de cadenas
def leerCantidadCadenas():
    """
    Solicita al usuario la cantidad de cadenas que desea validar.
    """
    try:
        cantidad = int(input("Por favor ingresa la cantidad de cadenas a validar: "))
        return cantidad
    except ValueError:
        print("Por favor ingrese un número válido para la cantidad de cadenas.")
        return 0


# Configuración de la interfaz gráfica
ventana = tk.Tk()
ventana.title("Validador de Expresiones Regulares")

# Configurar tamaño y centrar la ventana
ventana_width = 500
ventana_height = 410
screen_width = ventana.winfo_screenwidth()
screen_height = ventana.winfo_screenheight()

# Calcular la posición para centrar la ventana
position_top = int(screen_height / 2 - ventana_height / 2)
position_right = int(screen_width / 2 - ventana_width / 2)

ventana.geometry(f'{ventana_width}x{ventana_height}+{position_right}+{position_top}')

# Establecer un color de fondo claro
ventana.configure(bg="#f0f0f0")

# Título central con estilo
label_titulo = tk.Label(ventana, text="Validador de Expresiones Regulares", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#3D738B")
label_titulo.pack(pady=20)

# Crear un marco para los campos de entrada
frame = tk.Frame(ventana, bg="#f0f0f0")
frame.pack(pady=10)

# Crear campos de entrada con un estilo atractivo
label_expresion = tk.Label(frame, text="Expresión regular:", bg="#f0f0f0", fg="#555", font=("Arial", 9))
label_expresion.grid(row=0, column=0, pady=5, sticky="w")

entrada_expresion = tk.Entry(frame, width=35, font=("Arial", 10), bd=2, relief="solid")
entrada_expresion.grid(row=1, column=0, pady=5)

label_cant_cadenas = tk.Label(frame, text="Cadenas a validar:", bg="#f0f0f0", fg="#555", font=("Arial", 9))
label_cant_cadenas.grid(row=2, column=0, pady=5, sticky="w")

entrada_cant_cadenas = tk.Entry(frame, width=35, font=("Arial", 10), bd=2, relief="solid")
entrada_cant_cadenas.grid(row=3, column=0, pady=5)

# Listado para las entradas de las cadenas
entradas_cadenas = []

# Función para actualizar los campos de cadenas
def actualizarCampos():
    # Limpiar campos existentes
    for entrada in entradas_cadenas:
        entrada.grid_forget()

    # Crear nuevos campos según la cantidad de cadenas
    cantidad_cadenas = int(entrada_cant_cadenas.get())
    entradas_cadenas.clear()

    for i in range(cantidad_cadenas):
        label = tk.Label(frame, text=f"Cadena {i + 1}:", bg="#f0f0f0", fg="#555", font=("Arial", 9))
        label.grid(row=4 + i * 2, column=0, pady=5, sticky="w")
        entrada = tk.Entry(frame, width=35, font=("Arial", 10), bd=2, relief="solid")
        entrada.grid(row=5 + i * 2, column=0, pady=5)
        entradas_cadenas.append(entrada)

entrada_cant_cadenas.bind("<KeyRelease>", lambda event: actualizarCampos())

# Botón para ejecutar la validación con un diseño moderno
btn_validar = tk.Button(ventana, text="Validar", command=ejecutarCodigo, font=("Arial", 12), bg="#2AA1B7", fg="white", bd=0, relief="raised", padx=15, pady=10)
btn_validar.pack(pady=15)

ventana.mainloop()