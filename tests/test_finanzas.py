import unittest
import json
from app import create_app, db
from app.models import Socio, Nivel, Membresia

class FinanzasTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Crear datos de prueba
        nivel = Nivel(nombre='Test Level', orden=1)
        membresia = Membresia(nombre='Test Membership', clases_por_semana=3)
        db.session.add(nivel)
        db.session.add(membresia)
        db.session.commit()

        socio = Socio(folio='SW0001', nombre_completo='Juan Busqueda', email='juan@test.com', 
                      nivel_id=nivel.id, membresia_id=membresia.id)
        db.session.add(socio)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_buscar_socio_api(self):
        # Simular login
        with self.client as c:
            with c.session_transaction() as sess:
                sess['_user_id'] = '1' # Asumimos que el usuario 1 es admin
                sess['_fresh'] = True

            # 1. Búsqueda que encuentra un resultado
            response = self.client.get('/socios/api/buscar?q=Juan Busqueda')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['nombre'], 'Juan Busqueda')
            self.assertEqual(data[0]['folio'], 'SW0001')

            # 2. Búsqueda por folio
            response = self.client.get('/socios/api/buscar?q=SW0001')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['nombre'], 'Juan Busqueda')

            # 3. Búsqueda que no encuentra nada
            response = self.client.get('/socios/api/buscar?q=Pedro')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data), 0)

            # 4. Búsqueda con menos de 3 caracteres
            response = self.client.get('/socios/api/buscar?q=Ju')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data), 0)

if __name__ == '__main__':
    unittest.main()
