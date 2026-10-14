
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registroForm');
    const mensajeDiv = document.getElementById('mensaje');
    const crearBtn = document.getElementById('crearCuentaBtn');

     /*Click inmediato: marcar registro y redirigir directamente a inicio completo*/
    if (crearBtn) {
        crearBtn.addEventListener('click', function(e){
            
            if (crearBtn.disabled) return;
            e.preventDefault();
            try {
                localStorage.setItem('usuarioRegistrado', 'true');
                const nombre = document.getElementById('nombre') ? document.getElementById('nombre').value : '';
                if (nombre) localStorage.setItem('nombreUsuario', nombre);
            } catch (err) {
                console.warn('No se pudo guardar en localStorage', err);
            }
            window.location.href = 'index.html';
        });
    }
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        
        const password = document.getElementById('password').value;
        const confirmarPassword = document.getElementById('confirmar_password').value;
        
        if (password !== confirmarPassword) {
            mostrarMensaje('Las contraseñas no coinciden', 'error');
            return;
        }
        
        
        if (password.length < 6) {
            mostrarMensaje('La contraseña debe tener al menos 6 caracteres', 'error');
            return;
        }
        
        // Validación de documento (opcional)
        const documento = document.getElementById('documento').value;
        if (documento.length < 5) {
            mostrarMensaje('El documento debe tener al menos 5 caracteres', 'error');
            return;
        }
        
        // Obtener los datos del formulario
        const formData = new FormData(form);
        
        // Mostrar mensaje de carga
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Registrando...';
        submitBtn.disabled = true;
        
        // Enviar datos al servidor
        fetch('registro_usuario.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarMensaje('¡Registro exitoso! Redirigiendo...', 'success');
                form.reset();

                
                try {
                    localStorage.setItem('usuarioRegistrado', 'true');
                    const nombre = document.getElementById('nombre') ? document.getElementById('nombre').value : '';
                    if (nombre) localStorage.setItem('nombreUsuario', nombre);
                } catch (e) {
                    console.warn('Imposible escribir en localStorage:', e);
                }

                // Redirigir después de 2 segundos
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);
            } else {
                mostrarMensaje('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error de conexión con el servidor', 'error');
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });
    
    function mostrarMensaje(mensaje, tipo) {
        mensajeDiv.textContent = mensaje;
        mensajeDiv.className = tipo;
        
        if (tipo === 'success') {
            mensajeDiv.style.color = 'green';
            mensajeDiv.style.backgroundColor = '#e8f5e8';
        } else {
            mensajeDiv.style.color = 'red';
            mensajeDiv.style.backgroundColor = '#ffe8e8';
        }
        
        mensajeDiv.style.padding = '10px';
        mensajeDiv.style.borderRadius = '5px';
        mensajeDiv.style.margin = '10px 0';
        mensajeDiv.style.display = 'block';
        
        setTimeout(() => {
            mensajeDiv.textContent = '';
            mensajeDiv.style.display = 'none';
        }, 5000);
    }
});