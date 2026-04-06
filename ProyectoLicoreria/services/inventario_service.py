from conexion.conexion import db

# ════════════════════════════════════════════
# CLASE INVENTARIO (POO + Colecciones)
# ════════════════════════════════════════════
class Inventario:
    def __init__(self):
        self._productos = {}
        self._nombres_index = {}
        self._categorias_index = {}
        self._ids_set = set()

    def cargar_desde_db(self):
        # Importación diferida para evitar error circular
        from models import Producto 
        
        productos = Producto.query.all()
        
        # Reiniciamos todas las colecciones para una carga limpia
        self._productos = {}
        self._nombres_index = {}
        self._categorias_index = {}
        self._ids_set = set()

        for p in productos:
            # 1. Convertimos a diccionario (Capa de persistencia a Memoria)
            d = p.to_dict()
            
            # 2. Llenamos el diccionario principal y el conjunto de IDs
            self._productos[p.id] = d
            self._ids_set.add(p.id)
            
            # 3. Sincronizamos el índice de nombres (búsqueda rápida)
            self._nombres_index[p.nombre.lower()] = p.id
            
            # 4. Sincronizamos el índice de categorías (CRUCIAL PARA EVITAR ERRORES)
            cat = p.categoria
            if cat not in self._categorias_index:
                self._categorias_index[cat] = []
            self._categorias_index[cat].append(p.id)
        
        return self._productos

    def agregar_producto(self, producto):
        """Agrega un objeto Producto a las colecciones en memoria"""
        d = producto.to_dict()
        self._productos[producto.id] = d
        self._ids_set.add(producto.id)
        self._nombres_index[producto.nombre.lower()] = producto.id

        if producto.categoria not in self._categorias_index:
            self._categorias_index[producto.categoria] = []
        self._categorias_index[producto.categoria].append(producto.id)

    def eliminar_producto(self, id):
        """Elimina un producto de todas las colecciones — O(1)"""
        if id in self._ids_set:
            p = self._productos[id]
            # Limpiar índices
            self._nombres_index.pop(p['nombre'].lower(), None)
            
            if p['categoria'] in self._categorias_index:
                if id in self._categorias_index[p['categoria']]:
                    self._categorias_index[p['categoria']].remove(id)
            
            del self._productos[id]
            self._ids_set.discard(id)
            return True
        return False

    def actualizar_producto(self, id, cantidad=None, precio=None):
        if id not in self._ids_set:
            return False
        if cantidad is not None:
            if cantidad < 0: raise ValueError('La cantidad no puede ser negativa')
            self._productos[id]['stock'] = cantidad
            # Recalculamos el estado según el nuevo stock
            # Esto evita que el HTML muestre información desactualizada
            from models import Producto
            self._productos[id]['estado'] = "Agotado" if cantidad == 0 else ("Bajo" if cantidad < 5 else "Normal")
            
        if precio is not None:
            if precio <= 0: raise ValueError('El precio debe ser mayor a 0')
            self._productos[id]['precio'] = round(float(precio), 2)
        return True

    def buscar_por_nombre(self, nombre):
        """Búsqueda optimizada por nombre o marca"""
        nombre_min = nombre.lower()
        return [p for p in self._productos.values() 
                if nombre_min in p['nombre'].lower() or nombre_min in p['marca'].lower()]

    def mostrar_todos(self):
        """Retorna la lista completa de diccionarios para la tabla"""
        return list(self._productos.values())

    def total_productos(self):
        return len(self._ids_set)

    def productos_agotados(self):
        return [p for p in self._productos.values() if p['stock'] == 0]
    

    def validar_y_descontar(self, producto_id, cantidad):
        """Verifica stock en memoria y descuenta si es posible"""
        if producto_id in self._productos:
            stock_actual = self._productos[producto_id]['stock']
            if stock_actual >= cantidad:
                # Descontamos en la colección de memoria
                nuevo_stock = stock_actual - cantidad
                self._productos[producto_id]['stock'] = nuevo_stock
                # Actualizamos el estado (Agotado/Bajo/Normal)
                self._productos[producto_id]['estado'] = "Agotado" if nuevo_stock == 0 else ("Bajo" if nuevo_stock < 5 else "Normal")
                return True
        return False