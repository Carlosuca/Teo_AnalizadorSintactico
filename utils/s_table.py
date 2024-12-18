## Tabla de Simbolos extendida, incluyendo ambitos y valores iniciales (algunos)


class Identifier:
    def __init__(self,name,type,ivalue=None,parameters=None,line_no=None):
        self.name = name
        self.type = type
        self.ivalue = ivalue
        self.parameters = parameters
        self.usage_count = 0  
        self.line_no = line_no

    def __str__(self):
        return "ID {:16} Tipo: {:16} Inicial: {:16} Parametros:{:32} Linea:{:8}".format(
                str(self.name), str(self.type), str(self.ivalue), str(self.parameters) , str(self.line_no))

## Estructura de tabla de simbolos. Una tabla se crea por ambito y se enlazan.
## Almacena simbolos en un hash table y hace referencias al ambito superior e inferiores.
class SymbolTable:
    def __init__(self, scope, parent):
        self.scope = scope
        self.parent = parent ##Ambito superio
        self.symbols = {} ##Simbolos en el ambito actual
        self.children = {} ##Sub-ambitos
        self.block_counter = 0
        self.const_counter = 0

    ## REvisa si la variable no existe. De ser el caso, la crea y almacena
    def addEntry(self,name,type,line_no,ivalue=None,parameters=None):
        if name in self.symbols: return
        self.symbols[name] = Identifier(name,type,ivalue,parameters,line_no)

    def addScope(self,scope):
        if scope in self.children: return
        self.children[scope] = SymbolTable(scope,self)
    def check_empty(self,liste):
        for a in self.symbols:
            if self.symbols[a].usage_count == 0:
                liste.append("\n\nAdvertencia: la variable " + self.symbols[a].name + " ha sido declarado pero no es utilizada\nen la linea: " + str(self.symbols[a].line_no))
        for e in self.children:
            self.children[e].check_empty(liste)

    def increment_usage(self, identifier_name):
        """
        Incrementa el contador de uso de un identificador y devuelve el valor actual.
        
        :param identifier_name: El nombre del identificador cuyo uso se incrementará.
        :return: El nuevo valor de usage_count si el identificador existe, None si no.
        """
        # Búsqueda recursiva en el ámbito actual y sus hijos
        def search_and_increment(scope):
            # Verificar si el identificador está en el ámbito actual
            if identifier_name in scope.symbols:
                symbol = scope.symbols[identifier_name]
                if not hasattr(symbol, 'usage_count'):
                    symbol.usage_count = 0  # Inicializar en caso de que no exista
                symbol.usage_count += 1
                return symbol.usage_count

            # Recorrer sub-ámbitos (hijos)
            for child_scope in scope.children.values():
                result = search_and_increment(child_scope)
                if result:
                    return result

            return None  # Identificador no encontrado

        # Iniciar la búsqueda desde el ámbito actual
        return search_and_increment(self)

    #Formateo para vizualizar niveles de ambito
    def printString(self,l):
        out = ''
        for i in range(0,l-1):
                out += '\t'

        out += f"scope of {self.scope}\n"
        for s in self.symbols.keys():
            for e in range(0,l):
                out += '\t'
            out += str(self.symbols[s]) + '\n'
        for c in self.children:
            out += self.children[c].printString(l+1)
        return out

    def __str__(self):
        return self.printString(0)
    

    def exists_in_scope(self, scope_name, identifier_name):
        """
        Verifica si un identificador existe en el ámbito dado o en sus padres.
        
        :param scope_name: El nombre del ámbito donde iniciar la búsqueda.
        :param identifier_name: El nombre del identificador que se busca.
        :return: True si el identificador existe en el ámbito, False en caso contrario.
        """
        # Buscar el scope
        current_scope = self.find_scope(scope_name)
        if not current_scope:
            return False  # Ámbito no encontrado
        # Buscar en el scope actual y sus padres
        while current_scope:
            if identifier_name in current_scope.symbols:
                return True
            current_scope = current_scope.parent
        
        return False
    
    def is_declared(self, identifier_name,depth=-1):

        # Buscar el scope
        current_scope = self
        
        # Buscar en el scope actual y sus padres
        while current_scope:
            
            if identifier_name in current_scope.symbols:
                return True
            current_scope = current_scope.parent
            if depth == 0:
                break
            depth-=1
        
        return False
    
    def find_symbol(self, identifier_name,depth=-1):

        # Buscar el scope
        current_scope = self
        
        # Buscar en el scope actual y sus padres
        while current_scope:
            
            if identifier_name in current_scope.symbols:
                return current_scope.symbols[identifier_name]
            current_scope = current_scope.parent
            if depth == 0:
                break
            depth-=1
        
        return None

    def find_scope(self, scope_name):
        """
        Encuentra un ámbito a partir de su nombre, buscando de forma recursiva en los sub-ambitos.
        
        :param scope_name: Nombre del ámbito a buscar.
        :return: El ámbito (objeto SymbolTable) si lo encuentra, None en caso contrario.
        """
        if self.scope == scope_name:
            return self

        for child_scope in self.children.values():
            result = child_scope.find_scope(scope_name)
            if result:
                return result
        
        return None

    def get_symbol(self, identifier_name):

        if identifier_name in self.symbols:
                return self.symbols[identifier_name]
        
        # Recorrer sub-ámbitos (hijos)
        for child_scope in self.children.values():
            result = child_scope.get_symbol(identifier_name)
            if result:
                return result
        
        return None

block_counter = 0

def find_node_by_type(node, target_type, depth=-1):
    # Verifica si el nodo actual tiene el tipo deseado
        # print(node.type)
        

        if depth == 0:
            return None
        # Recurre en los hijos del nodo actual
        for child in node.children:
            if child.type == target_type:
                return child
            result = find_node_by_type(child, target_type, depth-1)
            if result is not None:  # Si se encuentra, se devuelve
                return result

        return None # Retorna None si no se encuentra el nodo

def build_symbol_table(node, symbol_table):
        # TODO: Parametros y valores inicialse de variables
        # print(find_node_by_type(node, 'DECLARACION'))
        
        if node.type == "INSTRUCCION_B" or node.type == "INSTRUCCION_C":
            inst_node = find_node_by_type(node, "INSTRUCCION_C", 1)
            if inst_node is not None:
                global block_counter
                block_counter += 1
                new_scope = f"{symbol_table.scope}_@blk_{str(node.children[0].value)}"
                symbol_table.addScope(new_scope)
                symbol_table.addScope(new_scope)
                blk_node = find_node_by_type(inst_node, "BLOQUE", 2)
                if blk_node is not None:
                    build_symbol_table(blk_node,symbol_table.children[new_scope])
                else:
                    build_symbol_table(find_node_by_type(inst_node, "INSTRUCCION", 1),symbol_table.children[new_scope])
                symbol_table = symbol_table.children[new_scope]

        if node.type == "INSTRUCCION_B" or node.type == "GLOBAL":
            type_node = find_node_by_type(node, "INSTRUCCION", 1)
            source = node
            if type_node is not None:
                source = type_node
                type_node = find_node_by_type(type_node, "TIPO", 1)
            else:
                type_node = find_node_by_type(node, "TIPO", 1)
            data_type = ""
            if type_node is not None:
                data_type = type_node.children[0].type
            else:
                type_node = find_node_by_type(source, "void", 1)
                data_type = 'void'
            if type_node is not None:
                
                id_node = find_node_by_type(source, 'identificador',1)
                
                while(id_node is not None):

                    
                    id_value = id_node.value
                    
                    func = find_node_by_type(source, "FUNCIONG_COLA", 2)
                    if func is None:
                        func = find_node_by_type(source, "FUNCION_COLA", 2)
                    if func is not None:
                        symbol_table.addEntry(id_value, "function " + data_type, "@" + id_value)
                        func_def = find_node_by_type(func, "BLOQUE", 1)
                        if func_def is not None:
                            new_scope = f"{symbol_table.scope}_{symbol_table.symbols[id_value].ivalue}"
                            symbol_table.addScope(new_scope)
                            node.addScope(new_scope)
                            # node.print_values()

                            param = find_node_by_type(node, "PARAMETROS", 2)
                            if param is not None:
                                build_symbol_table(param,symbol_table.children[new_scope])
                            build_symbol_table(func_def,symbol_table.children[new_scope])
                    else:
                        if type_node.type != "void":
                            symbol_table.addEntry(id_value,data_type)
                
                    
                    source = find_node_by_type(source, '_DECLARACION_CONT')

                    if(source is not None):
                        id_node = find_node_by_type(source, 'identificador')
                    else: 
                        id_node = None


        
        if node.type == "PARAMETROS" or node.type == "_PARAMETROS":
            type_node = find_node_by_type(node, "TIPO", 1)
            if type_node is not None:
                data_type = type_node.type
                id_node = find_node_by_type(node, "identificador", 1).value
                symbol_table.addEntry(id_node,data_type)
                next_param = find_node_by_type(node, "_PARAMETROS", 1)
                if next_param is not None:
                    build_symbol_table(next_param,symbol_table)


        if node.type == "_GLOBAL" or node.type == "BLOQUE":
            for child in node.children:
                build_symbol_table(child, symbol_table)

        if node.type == "PROGRAMA":
            build_symbol_table(find_node_by_type(node, "_GLOBAL", 1), symbol_table)
                

        return symbol_table

def construir_tabla(tree):
    # Tabla de símbolos

    # Construir la tabla
    global block_counter
    block_counter = 0
    symbol_table = build_symbol_table(find_node_by_type(tree, "_GLOBAL", 1), SymbolTable('global', None))
    symbol_table.addEntry("printf","function void","@printf")
    symbol_table.addEntry("scanf","function void","@scanf")
    tree.addScope('global')
    # node.print_values()
    # symbol_table = build_symbol_table(tree, SymbolTable('@global', None))

    # Imprime la tabla
    
    return symbol_table
    # # Imprimir usando tabulate
    # print(tabulate(symbol_table.transpose(), headers="keys", tablefmt="grid"))

