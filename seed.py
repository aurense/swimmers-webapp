from app import create_app, db
from app.models import Membresia, Tarifa, Horario, Socio, Inscripcion, Pago, User, Nivel
from datetime import time, datetime

# Crear instancia de la app para acceder a la BD
app = create_app()

def seed_database():
    with app.app_context():
        print("🌱 Iniciando sembrado de datos...")

        # 1. LIMPIEZA TOTAL (Opcional: borra todo para empezar limpio)
        print("⚠️  Borrando datos antiguos...")
        db.drop_all()
        db.create_all()

        # 2. MEMBRESÍAS
        print("   Creando Membresías...")
        plan_a = Membresia(nombre="Plan A (1 Clase/sem)", clases_por_semana=1)
        plan_b = Membresia(nombre="Plan B (2 Clases/sem)", clases_por_semana=2)
        plan_c = Membresia(nombre="Plan C (3 Clases/sem)", clases_por_semana=3)
        plan_f = Membresia(nombre="Plan F (6 Clases/sem)", clases_por_semana=6)
        
        db.session.add_all([plan_a, plan_b, plan_c, plan_f])
        db.session.commit() # Guardamos para obtener los IDs

        # 3. TARIFAS (Relacionadas con Membresías)
        print("   Creando Tarifas...")
        # Tarifas Plan A
        t1 = Tarifa(membresia_id=plan_a.id, nivel="Niños", costo_mensual=800, costo_anualidad=2000, costo_inscripcion=500)
        t2 = Tarifa(membresia_id=plan_a.id, nivel="Adultos", costo_mensual=900, costo_anualidad=2000, costo_inscripcion=500)
        
        # Tarifas Plan B
        t3 = Tarifa(membresia_id=plan_b.id, nivel="Niños", costo_mensual=1400, costo_anualidad=2000, costo_inscripcion=500)
        t4 = Tarifa(membresia_id=plan_b.id, nivel="Adultos", costo_mensual=1600, costo_anualidad=2000, costo_inscripcion=500)

        db.session.add_all([t1, t2, t3, t4])

        # 4. HORARIOS (Generación masiva)
        print("   Generando Horarios Semanales...")
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        horas_clase = [
            (time(16, 0), time(17, 0), "Niños"),  # 4pm a 5pm
            (time(17, 0), time(18, 0), "Niños"),  # 5pm a 6pm
            (time(18, 0), time(19, 0), "Adultos"), # 6pm a 7pm
            (time(19, 0), time(20, 0), "Adultos"), # 7pm a 8pm
        ]

        for dia in dias:
            for inicio, fin, nivel in horas_clase:
                h = Horario(
                    dia_semana=dia,
                    hora_inicio=inicio,
                    hora_fin=fin,
                    nivel=nivel,
                    capacidad_maxima=8 # Cupo estándar
                )
                db.session.add(h)
        
        db.session.commit()

        # 5. SOCIOS DE PRUEBA
        print("   Registrando Socios Dummy...")
        
        # Socio 1: Juanito (Niño, Plan B)
        juan = Socio(
            folio="SW0001",
            nombre_completo="Juanito Pérez",
            nivel="Niños",
            email="juan@test.com",
            membresia_id=plan_b.id,
            fecha_registro=datetime.utcnow()
        )

        # Socio 2: María (Adulto, Plan A)
        maria = Socio(
            folio="SW0002",
            nombre_completo="María López",
            nivel="Adultos",
            email="maria@test.com",
            membresia_id=plan_a.id,
            fecha_registro=datetime.utcnow()
        )

        db.session.add_all([juan, maria])
        db.session.commit()

        # 6. PAGOS INICIALES (Para probar estado financiero)
        print("   Registrando Pagos...")
        
        # Juan paga inscripción y anualidad
        pago1 = Pago(
            folio_recibo="REC-001",
            socio_id=juan.id,
            concepto_tipo="Anualidad",
            detalle_concepto="Anualidad 2025",
            monto_base=2000,
            total_cobrado=2000,
            metodo_pago="Efectivo"
        )
        
        db.session.add(pago1)
        db.session.commit()

        print("   Creando Usuarios del Sistema...")
        
        # Usuario Administrador
        admin = User(username='admin', role='admin')
        admin.set_password('admin123') # Contraseña simple para pruebas
        
        # Usuario Recepción
        recep = User(username='recepcion', role='recepcion')
        recep.set_password('1234')
        
        # Usuario Instructor
        profe = User(username='profe', role='instructor')
        profe.set_password('1234')
        
        db.session.add_all([admin, recep, profe])
        db.session.commit()

        print("   Creando Niveles...")
        n1 = Nivel(nombre="Bebés", orden=1)
        n2 = Nivel(nombre="Niños", orden=2)
        n3 = Nivel(nombre="Adultos", orden=3)

        db.session.add_all([n1, n2, n3])
        db.session.commit()

        print("✅ Base de datos sembrada con éxito.")
        print(f"   -> {Membresia.query.count()} Membresías")
        print(f"   -> {Horario.query.count()} Horarios")
        print(f"   -> {Socio.query.count()} Socios")
        print("✅ Usuarios creados: admin / recepcion / profe")

if __name__ == '__main__':
    seed_database()