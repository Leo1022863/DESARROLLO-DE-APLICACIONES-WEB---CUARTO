#Clase producto
class Producto: 
    def __init__(self, id_producto, nombre, descripcion, precio, cantidad):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.cantidad = cantidad

    #tupla
    def to_tuple(self):
        return (self.id_producto, self.nombre, self.descripcion, self.precio, self.cantidad)
    
    #dict
    def to_dict(self):
        return {
            'id_producto': self.id_producto,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'cantidad': self.cantidad
        }