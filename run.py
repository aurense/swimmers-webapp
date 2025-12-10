import os

from app import create_app, db
from app.models import Socio, Horario, Membresia, Tarifa, Pago, Inscripcion, Asistencia

app = create_app()

# Esto habilita el contexto de la shell para pruebas rápidas
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'Socio': Socio, 
        'Horario': Horario, 
        'Membresia': Membresia, 
        'Tarifa': Tarifa,
        'Pago': Pago,
        'Inscripcion': Inscripcion,
        'Asistencia': Asistencia
    }

if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 80)),debug=True)