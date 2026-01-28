
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-cerrar alertas después de 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Confirmar eliminación
    setupDeleteConfirmation();
    
    // Búsqueda en tiempo real
    setupLiveSearch();
});


function setupDeleteConfirmation() {
    var deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm') || '¿Estás seguro de realizar esta acción?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}


function setupLiveSearch() {
    var searchInputs = document.querySelectorAll('[data-live-search]');
    searchInputs.forEach(function(input) {
        var timeout = null;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            var query = this.value;
            var endpoint = this.getAttribute('data-live-search');
            var targetId = this.getAttribute('data-target');
            
            if (query.length < 2) {
                return;
            }
            
            timeout = setTimeout(function() {
                fetch(endpoint + '?q=' + encodeURIComponent(query))
                    .then(response => response.json())
                    .then(data => {
                        if (targetId) {
                            updateSearchResults(targetId, data);
                        }
                    })
                    .catch(error => console.error('Error en búsqueda:', error));
            }, 300);
        });
    });
}

function updateSearchResults(targetId, data) {
    var container = document.getElementById(targetId);
    if (!container) return;
    
    container.innerHTML = '';
    
    if (data.length === 0) {
        container.innerHTML = '<p class="text-muted p-3">No se encontraron resultados</p>';
        return;
    }
    
    data.forEach(function(item) {
        var div = document.createElement('div');
        div.className = 'p-2 border-bottom cursor-pointer';
        div.textContent = item.nombre || item.descripcion || JSON.stringify(item);
        div.addEventListener('click', function() {
            // Implementar selección
            console.log('Seleccionado:', item);
        });
        container.appendChild(div);
    });
}


function cargarMascotas(propietarioId, selectId) {
    var select = document.getElementById(selectId);
    if (!select) return;
    
    select.innerHTML = '<option value="">Cargando...</option>';
    select.disabled = true;
    
    fetch('/mascotas/api/by-propietario/' + propietarioId)
        .then(response => response.json())
        .then(data => {
            select.innerHTML = '<option value="">Seleccione mascota...</option>';
            data.forEach(function(mascota) {
                var option = document.createElement('option');
                option.value = mascota.id;
                option.textContent = mascota.nombre + ' (' + mascota.especie + ')';
                select.appendChild(option);
            });
            select.disabled = false;
        })
        .catch(error => {
            console.error('Error:', error);
            select.innerHTML = '<option value="">Error al cargar</option>';
        });
}


function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}


function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return true;
    
    var isValid = true;
    var requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}


function showLoading(elementId) {
    var element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
    }
}

function hideLoading(elementId) {
    var element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

// Exportar funciones para uso global
window.VetCare = {
    cargarMascotas: cargarMascotas,
    formatDate: formatDate,
    formatDateTime: formatDateTime,
    validateForm: validateForm,
    showLoading: showLoading,
    hideLoading: hideLoading
};
