let productos = [
    {
        nombre: "Laptop HP",
        precio: 899.99,
        descripcion: "Laptop de alto rendimiento con procesador Intel Core i7 y 16GB RAM"
    },
    {
        nombre: "Mouse Inalámbrico",
        precio: 25.50,
        descripcion: "Mouse ergonómico con conexión Bluetooth y batería de larga duración"
    },
    {
        nombre: "Teclado Mecánico",
        precio: 79.99,
        descripcion: "Teclado mecánico RGB con switches azules, ideal para gaming"
    },
    {
        nombre: "Monitor 24 pulgadas",
        precio: 189.99,
        descripcion: "Monitor Full HD con tecnología IPS y frecuencia de 75Hz"
    }
];

// Función para renderizar los productos
function renderizarProductos() {
    const lista = document.getElementById('listaProductos');
    lista.innerHTML = ''; // Limpiar la lista antes de renderizar

    productos.forEach(producto => {
        const li = document.createElement('li');
        li.innerHTML = `
                    <div class="producto-nombre">${producto.nombre}</div>
                    <div class="producto-precio">$${producto.precio.toFixed(2)}</div>
                    <div class="producto-descripcion">${producto.descripcion}</div>
                `;
        lista.appendChild(li);
    });
}

// Función para mostrar el formulario
function mostrarFormulario() {
    document.getElementById('formulario').style.display = 'block';
    document.getElementById('btnAgregar').style.display = 'none';
}

// Función para ocultar el formulario
function ocultarFormulario() {
    document.getElementById('formulario').style.display = 'none';
    document.getElementById('btnAgregar').style.display = 'inline-block';
    limpiarFormulario();
}

// Función para limpiar los campos del formulario
function limpiarFormulario() {
    document.getElementById('inputNombre').value = '';
    document.getElementById('inputPrecio').value = '';
    document.getElementById('inputDescripcion').value = '';
}

// Función para guardar el nuevo producto
function guardarProducto() {
    const nombre = document.getElementById('inputNombre').value.trim();
    const precio = parseFloat(document.getElementById('inputPrecio').value);
    const descripcion = document.getElementById('inputDescripcion').value.trim();

    // Validar que los campos no estén vacíos
    if (nombre === '' || isNaN(precio) || precio <= 0 || descripcion === '') {
        alert('Por favor, completa todos los campos correctamente.');
        return;
    }

    const nuevoProducto = {
        nombre: nombre,
        precio: precio,
        descripcion: descripcion
    };

    productos.push(nuevoProducto);
    renderizarProductos();
    ocultarFormulario();
}

// Event listeners
document.getElementById('btnAgregar').addEventListener('click', mostrarFormulario);
document.getElementById('btnGuardar').addEventListener('click', guardarProducto);
document.getElementById('btnCancelar').addEventListener('click', ocultarFormulario);

// Renderizar productos al cargar la página
renderizarProductos();