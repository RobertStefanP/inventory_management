import re
import sys

class Producto:
    def __init__(self, nombre, categoria, precio, cantidad):
        self._nombre = nombre
        self._categoria = categoria
        self._precio = precio
        self._cantidad = cantidad
    
    def get_nombre(self):
        return self._nombre

    def get_categoria(self):
        return self._categoria

    def get_precio(self):
        return self._precio

    def get_cantidad(self):
        return self._cantidad    
    
    def set_nombre(self, nombre):
        if isinstance(nombre, str) and nombre.strip():
            self._nombre = nombre

    def set_categoria(self, categoria):
        if isinstance(categoria, str) and categoria.strip():
            self._categoria = categoria

    def set_precio(self, precio):
        if isinstance(precio, (int, float)) and precio > 0:
            self._precio = precio

    def set_cantidad(self, cantidad):
        if isinstance(cantidad, (int, float)) and cantidad >= 0:
            self._cantidad = cantidad
       
    def mostrar_info(self):
        print(f"\nProducto: {self._nombre}\n"
            f"Categoria: {self._categoria}\n"
            f"Precio: {self._precio}\n"
            f"Cantidad: {self._cantidad}\n")
        
class Inventario:
    def __init__(self):
        self._inventario = [] 
        
    def agregar_producto(self, producto): 
        if not self.producto_existente(producto.get_nombre()):
            self._inventario.append(producto)
            return True 
        return False 
        
    def producto_existente(self, nombre_producto): 
        for producto in self._inventario:
            if producto.get_nombre().lower() == nombre_producto.lower():
                return True
        return False    

    def mostrar_inventario(self):  
        if not self._inventario:
            return None
        else:
            return self._inventario  
                
    def actualizar_producto(self, nombre_producto, nuevo_precio=None, nueva_cantidad=None): 
        for producto in self._inventario:
            if producto.get_nombre().lower() == nombre_producto.lower():
                if nuevo_precio is not None:
                    producto.set_precio(nuevo_precio)
                if nueva_cantidad is not None:
                    producto.set_cantidad(nueva_cantidad)
                return producto
        return None

    def eliminar_producto(self, nombre_producto): 
        for producto in self._inventario:
            if producto.get_nombre().lower() == nombre_producto.lower():
                self._inventario.remove(producto)
                return True
        return False
    
    def buscar_producto(self, nombre_producto):  
        for producto in self._inventario:
            if producto.nombre == nombre_producto:
                return producto 
        return None 

inventario = Inventario()  
            
while True:
    volver_al_menu = False         
    try:
        menu = False 
        print("\n-----MENU INVENTARIO-----\n")                        
        print("1. Agregar producto")
        print("2. Actualizar producto")
        print("3. Eliminar producto")
        print("4. Mostrar inventario")
        print("5. Buscar un producto")    
        print("6. Salir")   
        
        opcion = int(input("\nElige una opcion: ")) 
                     
        if opcion == 1:                    
            while not volver_al_menu:                
                nombre = input("  Introduzca el produco que desea agregar: ") 
                if inventario.producto_existente(nombre):  
                    print("\n--ERROR! El producto ya existe en el inventario.")                                                         
                    while True:
                        print("  Elija opcion:")
                        print("  1 -Intentar con otro producto.\n  2 -Volver al menu principal.\n")
                        opcion = input("  Opcion 1 o 2: ")
                        if opcion == "1":
                            break
                        elif opcion == "2":
                            print("Volviendo al menú principal")
                            nombre = None 
                            volver_al_menu = True                                
                            break
                        else:
                            print("--ERROR! Opcion no valida, elegir 1 o 2.")
                            continue
                    if volver_al_menu:  
                        break
                else:    
                    if re.fullmatch(r"[a-zA-Z0-9\s]+", nombre) and nombre.strip() != "":
                            break                         
                    else: 
                        print("\n--ERROR! El espacio no puede ser vacio o tener caracteres especiales.") 
                                                       
            if nombre and not volver_al_menu:                                                                                   
                while not volver_al_menu:                    
                    categoria = input("\n  Introduzca la categoria: ")  
                                                        
                    if re.fullmatch(r"[a-zA-Z0-9\s]+", categoria) and categoria.strip() != "":
                        break
                    else:
                        print("\n--ERROR! El espacio no puede ser vacio o tener caracteres especiales.")                         
                        while True:
                            print(" 1 -Reintroducir categoria.\n 2 -Volver al menu principal.\n")
                            reintento_o_menuprincipal = input("  Opcion 1 o 2: ")
                                            
                            if reintento_o_menuprincipal == "1":
                                break                                
                            elif reintento_o_menuprincipal == "2":
                                print("Volviendo al menú principal")
                                categoria = None
                                volver_al_menu = True
                                break                                                                        
                            else:
                                print("--ERROR! Elija 1 o 2.")
                                continue 
                            
                    if volver_al_menu:
                        break  
                                                                     
                if nombre and categoria and not volver_al_menu:  
                    while not volver_al_menu:
                        try:                                    
                            precio = input("\n  Precio del producto: ")                     
                            if int(precio) > 0 and precio.isnumeric():
                                break 
                            else:                                
                                while True: 
                                    print("1 -Reintentar\n2 -Volver al menu principal")
                                    reintentar_o_menu = input("\n   Opcion 1 o 2: ")

                                    if reintentar_o_menu == "1":
                                        break  
                                    elif reintentar_o_menu == "2":
                                        print("Volviendo al menu principal.")
                                        precio = None
                                        volver_al_menu = True
                                        break  
                                    else:
                                        print("--ERROR! Elija 1 o 2")
                                        continue      
                                                                        
                            if volver_al_menu: 
                                break    
                            
                        except ValueError:
                            print("\n--ERROR! Introducir un valor numerico valido.")   
                                                                                
                            while True: 
                                print("1 -Reintentar \n2 -Volver al menu principal")
                                reintentar_o_menu = input("\n   Opción 1 o 2: ")

                                if reintentar_o_menu == "1":
                                    break  
                                elif reintentar_o_menu == "2":
                                    print("Volviendo al menu principal.")
                                    precio = None
                                    volver_al_menu = True
                                    break  
                                else:
                                    print("--ERROR! Opcion no valida, elija 1 o 2.")
                                    continue  
                                     
                    if precio is not None and not volver_al_menu:
                        cantidad = None  
                        while not volver_al_menu:  
                            try:
                                cantidad = float(input("\n  Introduzca la cantidad: ")) 
                                if cantidad > 0:
                                    break  
                                else:
                                    print("--ERROR! La cantidad no puede ser 0 o negativa.")
                            
                                    while True:  
                                        print("\n  Reintentar introducir cantidad o salir al menú principal?")
                                        print("1 -Reintentar introducir cantidad\n2 -Volver al menú principal")
                                        reintentar_o_menu = input("\n   Opción 1 o 2: ")

                                        if reintentar_o_menu == "1":                                            
                                            break 
                                        elif reintentar_o_menu == "2":
                                            print("Volviendo al menú principal.")
                                            cantidad = None  
                                            volver_al_menu = True
                                            break  
                                        else:
                                            print("--ERROR! Opción no válida, elija 1 o 2.")
                                            continue                              
                                if volver_al_menu:
                                    break                                
                            except ValueError:
                                print("--ERROR! Introducir un valor numerico valido.")
                                
                    if precio is not None and cantidad is not None:
                        producto = Producto(nombre, categoria, precio, cantidad)  
                        if inventario.agregar_producto(producto):  
                            print(f"\nProducto '{nombre}' agregado correctamente al inventario.") 
                        else:
                            print(f"--ERROR! El producto '{producto.get_nombre()}' ya existe en el inventario.")                             
                        inventario.mostrar_inventario()  
                                                                 
        elif opcion ==2:                                                       
            while not volver_al_menu:
                try:
                    nombre_producto = input("\n  Introduzca el nombre del producto a actualizar: ")            
                    if inventario.producto_existente(nombre_producto): 
                        while True:                                                                   
                            nuevo_precio = input("  Introduzca el nuevo precio (dejar vacío para no cambiar): ")
                            
                            if nuevo_precio.strip() == "":
                                nuevo_precio = None
                                break
                            try:
                                nuevo_precio = float(nuevo_precio)
                                if nuevo_precio == 0:
                                    print("--ERROR! El precio no puede ser 0. Inténtelo de nuevo.")
                                    continue  
                                else:
                                    break  
                            except ValueError:
                                print("\n--ERROR! Debe introducir un valor numérico válido.")
                                continue  
                        while True:    
                            nueva_cantidad = input("\n  Introduzca la nueva cantidad (dejar vacío para no cambiar): ")
                            
                            if nueva_cantidad.strip() == "":
                                nueva_cantidad = None
                                break 
                            try:
                                nueva_cantidad = float(nueva_cantidad)
                                if nueva_cantidad <= 0:
                                    print("--ERROR! La cantidad debe ser mayor que 0. Inténtelo de nuevo.")
                                    continue
                                else:
                                    break
                                
                            except ValueError:
                                print("--ERROR! Debe introducir un valor numérico válido.")                                                                                
                        inventario.actualizar_producto(nombre_producto, nuevo_precio, nueva_cantidad)
                        print(f"Producto '{nombre_producto}' actualizado correctamente.")
                        break                                 
                    else:
                        while True: 
                            print("\n--ERROR! Producto no encontrado, reintentar a actualizar producto o salir al menu principal?")
                            print("\n 1 -Reintentar actualizar producto.\n 2 -Volver al menu principal.")
                            reintento_o_menuprincipal = input("\n   Opcion 1 o 2: ")
                            if reintento_o_menuprincipal == "1":                                
                                break
                            elif reintento_o_menuprincipal == "2":
                                print("Volviendo al menu principal.")
                                volver_al_menu = True
                                break
                            else:
                                print("--ERROR! Opcion no valida, elige 1 o 2.")
                                continue
                    if volver_al_menu:
                        break  
                                       
                except ValueError:
                    print("--ERROR! Debe introducir un valor numérico válido.")    
                                                                                                         
        elif opcion == 3:
            while not volver_al_menu:                
                nombre_producto = input("  Introduzca el nombre del producto que desea eliminar: ")                   
                if inventario.eliminar_producto(nombre_producto):
                    print(f"Producto '{nombre_producto}' eliminado correctamente.")
                    break
                else:
                    while True:
                        print("\n--ERROR! Producto no encontrado, reintentar o salir al menú principal?\n 1 -Reintentar a eliminar.\n 2 -Volver al menú principal.")
                        reintento_o_menuprincipal = input("\n   Opción 1 o 2: ")
                        if reintento_o_menuprincipal == "1":
                            break  
                        elif reintento_o_menuprincipal == "2":
                            volver_al_menu = True
                            print("Volviendo al menu principal.")
                            break  
                        else:
                            print("--ERROR! Opción no válida, elige 1 o 2.")
                            continue                            
                if volver_al_menu:
                    break                    
                           
        elif opcion == 4:
            inventario_actual = inventario.mostrar_inventario()            
            if not inventario_actual: 
                print("\n  El inventario está vacío.")                
            else:                
                print("\n  Inventario:")
                for producto in inventario_actual:
                    producto.mostrar_info()  
                    
        elif opcion == 5:
            while not volver_al_menu:                
                nombre_producto = input("  Introduzca el nombre del producto que desea buscar: ")
                producto = inventario.buscar_producto(nombre_producto) 
                if producto:                      
                    producto.mostrar_info() 
                    break  
                
                else:                         
                    while True:
                        print("\n--ERROR! Producto no encontrado, reintentar o salir al menú principal?\n 1 -Reiniciar la busqueda\n 2 -Volver al menú principal")
                        reintento_o_menuprincipal = input("\n   Opción 1 o 2: ")
                        if reintento_o_menuprincipal == "1":
                            break  
                        elif reintento_o_menuprincipal == "2":
                            volver_al_menu = True
                            print("Volviendo al menú principal.")
                            break  
                        else:
                            print("--ERROR! Opción no válida, elige 1 o 2.")
                            continue
                if volver_al_menu:  
                    break           
                                        
        elif opcion == 6:  
            print("  Saliendo del programa.")
            sys.exit()
            
        else:
            print("--ERROR! Debe introducir un número válido del 1 al 6.")    
                            
    except ValueError:
        print("--ERROR! Debe introducir un numero.")