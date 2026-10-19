import os
import unittest
from datetime import date

# Point the app at an in-memory database before it is imported, so the test
# runs never touch the development database.
os.environ['DATABASE_URI'] = 'sqlite:///:memory:'

from app import app
from app.models import db, Workout, Exercise


class WorkoutTrackerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_and_get_workout(self):
        response = self.app.post('/workouts', json={
            'date': '2026-07-27',
            'duration_minutes': 45,
            'notes': 'Full body training'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['date'], '2026-07-27')
        self.assertEqual(data['duration_minutes'], 45)
        self.assertEqual(data['notes'], 'Full body training')
        self.assertIn('id', data)

        workout_id = data['id']
        response = self.app.get(f'/workouts/{workout_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['date'], '2026-07-27')
        self.assertEqual(data['exercises'], [])

    def test_create_and_get_exercise(self):
        response = self.app.post('/exercises', json={
            'name': 'Push Up',
            'category': 'Strength',
            'equipment_needed': False
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], 'Push Up')
        self.assertEqual(data['category'], 'Strength')
        self.assertFalse(data['equipment_needed'])

        exercise_id = data['id']
        response = self.app.get(f'/exercises/{exercise_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Push Up')

    def test_add_exercise_to_workout(self):
        with app.app_context():
            exercise = Exercise(name='Burpee', category='Cardio', equipment_needed=False)
            workout = Workout(date=date(2026, 7, 27), duration_minutes=50, notes='Full Body')
            db.session.add_all([exercise, workout])
            db.session.commit()
            exercise_id = exercise.id
            workout_id = workout.id

        response = self.app.post(
            f'/workouts/{workout_id}/exercises',
            json={'exercise_id': exercise_id, 'sets': 3, 'reps': 10}
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['id'], workout_id)
        self.assertEqual(data['date'], '2026-07-27')
        self.assertEqual(len(data['exercises']), 1)
        self.assertEqual(data['exercises'][0]['exercise_id'], exercise_id)
        self.assertEqual(data['exercises'][0]['sets'], 3)
        self.assertEqual(data['exercises'][0]['reps'], 10)

        response = self.app.get(f'/workouts/{workout_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['exercises']), 1)
        self.assertEqual(data['exercises'][0]['exercise_id'], exercise_id)

    def test_workout_not_found(self):
        response = self.app.get('/workouts/9999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 'Workout not found')

    def test_exercise_not_found(self):
        response = self.app.get('/exercises/9999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 'Exercise not found')


if __name__ == '__main__':
    unittest.main()
