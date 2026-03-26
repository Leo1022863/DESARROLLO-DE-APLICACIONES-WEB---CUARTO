

// Obtener elementos del DOM
const form = document.getElementById('registroForm');
const nombre = document.getElementById('nombre');
const email = document.getElementById('email');
const password = document.getElementById('password');
const confirmPassword = document.getElementById('confirmPassword');
const edad = document.getElementById('edad');
const btnSubmit = document.getElementById('btnSubmit');

// Estado de validación de cada campo
const validationState = {
    nombre: false,
    email: false,
    password: false,
    confirmPassword: false,
    edad: false
};

// Función para validar nombre
function validarNombre() {
    const valor = nombre.value.trim();
    const esValido = valor.length >= 3;

    actualizarEstado(nombre, 'nombre', esValido);
    validationState.nombre = esValido;
    verificarFormulario();
}

// Función para validar email
function validarEmail() {
    const valor = email.value.trim();
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const esValido = regex.test(valor);

    actualizarEstado(email, 'email', esValido);
    validationState.email = esValido;
    verificarFormulario();
}

// Función para validar contraseña
function validarPassword() {
    const valor = password.value;
    const tieneNumero = /\d/.test(valor);
    const tieneEspecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(valor);
    const longitudCorrecta = valor.length >= 8;
    const esValido = tieneNumero && tieneEspecial && longitudCorrecta;

    actualizarEstado(password, 'password', esValido);
    validationState.password = esValido;

    // Revalidar confirmación si ya hay algo escrito
    if (confirmPassword.value) {
        validarConfirmPassword();
    }

    verificarFormulario();
}

// Función para validar confirmación de contraseña
function validarConfirmPassword() {
    const valor = confirmPassword.value;
    const esValido = valor === password.value && valor !== '';

    actualizarEstado(confirmPassword, 'confirmPassword', esValido);
    validationState.confirmPassword = esValido;
    verificarFormulario();
}

// Función para validar edad
function validarEdad() {
    const valor = parseInt(edad.value);
    const esValido = !isNaN(valor) && valor >= 18;

    actualizarEstado(edad, 'edad', esValido);
    validationState.edad = esValido;
    verificarFormulario();
}

// Función para actualizar el estado visual de un campo
function actualizarEstado(campo, nombreCampo, esValido) {
    const errorElement = document.getElementById(`error${nombreCampo.charAt(0).toUpperCase() + nombreCampo.slice(1)}`);
    const successElement = document.getElementById(`success${nombreCampo.charAt(0).toUpperCase() + nombreCampo.slice(1)}`);

    if (campo.value === '') {
        campo.classList.remove('valid', 'invalid');
        errorElement.classList.remove('show');
        successElement.classList.remove('show');
    } else if (esValido) {
        campo.classList.remove('invalid');
        campo.classList.add('valid');
        errorElement.classList.remove('show');
        successElement.classList.add('show');
    } else {
        campo.classList.remove('valid');
        campo.classList.add('invalid');
        errorElement.classList.add('show');
        successElement.classList.remove('show');
    }
}

// Función para verificar si todo el formulario es válido
function verificarFormulario() {
    const todoValido = Object.values(validationState).every(estado => estado === true);
    btnSubmit.disabled = !todoValido;
}

// Event listeners para validación en tiempo real
nombre.addEventListener('input', validarNombre);
email.addEventListener('input', validarEmail);
password.addEventListener('input', validarPassword);
confirmPassword.addEventListener('input', validarConfirmPassword);
edad.addEventListener('input', validarEdad);

// Event listener para el envío del formulario
form.addEventListener('submit', function (e) {
    e.preventDefault();

    if (Object.values(validationState).every(estado => estado === true)) {
        alert('¡Formulario enviado con éxito! \n\nTodos los datos son válidos.');
        console.log('Datos del formulario:', {
            nombre: nombre.value,
            email: email.value,
            edad: edad.value
        });
    }
});

// Event listener para reiniciar el formulario
form.addEventListener('reset', function () {
    // Resetear estados visuales
    const campos = [nombre, email, password, confirmPassword, edad];
    campos.forEach(campo => {
        campo.classList.remove('valid', 'invalid');
    });

    // Ocultar mensajes
    document.querySelectorAll('.error-message, .success-message').forEach(msg => {
        msg.classList.remove('show');
    });

    // Resetear estado de validación
    Object.keys(validationState).forEach(key => {
        validationState[key] = false;
    });

    // Deshabilitar botón de envío
    btnSubmit.disabled = true;
});