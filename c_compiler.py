from c_lexer import *
from c_parser import *

if __name__ == '__main__':
    lista, tabla = identificar_tokens(analizador, r'C:\Users\oscar\Dropbox\PC\Documents\Teo_AnalizadorSintactico\test\test1.c')

    print('Lista de tokens....')
    print("\n")
    imprimir_tokens(lista)
    print("\n")
    arbol = construir_arbol(lista)
    print(arbol)
    # print("Tabla de simbolos...")
    # print("\n")
    # imprimir_tabla(tabla)
    print('\n')
    input("Presiona enter para salir")