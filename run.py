"""
VetCare Pro - Sistema de Gestión de Veterinaria
Punto de entrada de la aplicación
"""
from app import create_app, db

# Crear la instancia de la aplicación
app = create_app('development')

if __name__ == '__main__':
    # Crear las tablas si no existen
    with app.app_context():
        db.create_all()
        print("✓ Base de datos verificada/creada correctamente")
    
    # Ejecutar el servidor de desarrollo
    print("\n" + "="*50)
    print("🐾 VetCare Pro - Sistema de Gestión de Veterinaria")
    print("="*50)
    print("→ Servidor iniciado en: http://localhost:5000")
    print("→ Modo: Desarrollo")
    print("→ Para detener: Ctrl + C")
    print("="*50 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
