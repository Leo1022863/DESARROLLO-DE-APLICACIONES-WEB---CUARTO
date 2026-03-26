from flask import Flask, render_template, url_for, request, redirect, flash
app = Flask(__name__)
#ruta principal
@app.route('/')
def inicio():
    return render_template('index.html')

#ruta del about
@app.route('/about')
def about():
    return render_template('about.html')

#ruta de contacto
@app.route('/contact')
def contact():
    return render_template('contact.html')

#ruta de productos
@app.route('/products')
def products():
    return render_template('products.html')



"""
#ruta con parametro
@app.route('/usuario/<nombre>')
def saludo(nombre):
    return f"Bienvenido estas en mi clase, {nombre}"

#ruta de un producto
@app.route('/producto/<int:id>')
def producto(id):
    return f"El producto con id {id} se encuentra en stock"

#ruta de facturacion
@app.route('/facturacion')
def factura():
    return 'Pagina de facturacion, el total a pagar'

#ruta de formulario
@app.route('/formulario')
def formulario():
    return '''
    <form action="/saludo" method="post">
        <input type="text" name="nombre" placeholder="Ingresa tu nombre">
        <input type="submit" value="Enviar">
    </form>
    '''

"""
if __name__ == '__main__':
    app.run(debug=True)

