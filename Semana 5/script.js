
        // Referencias a elementos del DOM
        const urlInput = document.getElementById('urlInput');
        const addBtn = document.getElementById('addBtn');
        const deleteBtn = document.getElementById('deleteBtn');
        const gallery = document.getElementById('gallery');
        
        let selectedImage = null;
        let imageCounter = 0;

        // URLs de ejemplo para demostración
        const defaultImages = [
            'https://upload.wikimedia.org/wikipedia/commons/7/7f/Ubuntu_25.10_default_desktop_-_English.png',
            'https://i.redd.it/i-created-a-pfsense-central-monitoring-management-dashboard-v0-7k8d1urk39bd1.jpg?width=1777&format=pjpg&auto=webp&s=e0f070a9a16d5b302558a3ac9de10b13af2d6815',
            'https://img.youtube.com/vi/vXdtGCytLgw/maxresdefault.jpg',
            'https://i.redd.it/myj5i87dohza1.png'
        ];

        // Función para agregar imagen
        function addImage(url) {
            if (!url || url.trim() === '') {
                alert('Por favor ingresa una URL válida');
                return;
            }

            // Eliminar el estado vacío si existe querySelector
            const emptyState = gallery.querySelector('.empty-state');
            if (emptyState) {
                emptyState.remove();
            }

            // Crear contenedor de la imagen createElement
            const galleryItem = document.createElement('div');
            galleryItem.className = 'gallery-item';
            galleryItem.dataset.id = imageCounter++;

            // Crear elemento de imagen
            const img = document.createElement('img');
            img.src = url;
            img.alt = `Imagen ${galleryItem.dataset.id}`;
            
            // Manejar error de carga
            img.onerror = () => {
                alert('No se pudo cargar la imagen. Verifica la URL.');
                galleryItem.remove();
                checkEmptyGallery();
            };

            // Agregar evento de clic para seleccionar addEventListener
            galleryItem.addEventListener('click', () => selectImage(galleryItem));

            // Agregar imagen al contenedor y contenedor a la galería
            galleryItem.appendChild(img);
            gallery.appendChild(galleryItem);

            // Limpiar input
            urlInput.value = '';
            urlInput.focus();
        }

        // Función para seleccionar imagen
        function selectImage(item) {
            // Deseleccionar imagen anterior
            if (selectedImage) {
                selectedImage.classList.remove('selected');
            }

            // Si se hace clic en la misma imagen, deseleccionar
            if (selectedImage === item) {
                selectedImage = null;
                deleteBtn.disabled = true;
            } else {
                // Seleccionar nueva imagen
                selectedImage = item;
                selectedImage.classList.add('selected');
                deleteBtn.disabled = false;
            }
        }

        // Función para eliminar imagen seleccionada
        function deleteSelectedImage() {
            if (!selectedImage) return;

            selectedImage.classList.add('removing');
            
            setTimeout(() => {
                selectedImage.remove();
                selectedImage = null;
                deleteBtn.disabled = true;
                checkEmptyGallery();
            }, 500);
        }

        // Función para verificar si la galería está vacía
        function checkEmptyGallery() {
            const images = gallery.querySelectorAll('.gallery-item');
            if (images.length === 0) {
                gallery.innerHTML = `
                    <div class="empty-state">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <h3>No hay imágenes en la galería</h3>
                        <p>Agrega una URL de imagen para comenzar</p>
                    </div>
                `;
            }
        }

        // Event Listeners
        addBtn.addEventListener('click', () => {
            addImage(urlInput.value);
        });

        deleteBtn.addEventListener('click', deleteSelectedImage);

        // Manejar Enter en el input
        urlInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                addImage(urlInput.value);
            }
        });

        // Atajos de teclado globales
        document.addEventListener('keydown', (e) => {
            // Delete o Backspace para eliminar imagen seleccionada
            if ((e.key === 'Delete' || e.key === 'Backspace') && selectedImage) {
                e.preventDefault();
                deleteSelectedImage();
            }
            
            // Escape para deseleccionar
            if (e.key === 'Escape' && selectedImage) {
                selectedImage.classList.remove('selected');
                selectedImage = null;
                deleteBtn.disabled = true;
            }
        });

        // Cargar imágenes de ejemplo al inicio
        window.addEventListener('load', () => {
            defaultImages.forEach(url => addImage(url));
        });