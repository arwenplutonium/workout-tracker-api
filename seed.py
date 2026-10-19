#!/usr/bin/env python3

from datetime import date, timedelta

from app import app
from app.models import db, Workout, Exercise, WorkoutExercise

with app.app_context():
    print("Clearing tables...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print("Seeding exercises...")
    squat = Exercise(name='Back Squat', category='Strength', equipment_needed=True)
    push_up = Exercise(name='Push Up', category='Strength', equipment_needed=False)
    plank = Exercise(name='Plank', category='Core', equipment_needed=False)
    rowing = Exercise(name='Rowing Machine', category='Cardio', equipment_needed=True)
    lunge = Exercise(name='Walking Lunge', category='Mobility', equipment_needed=False)

    db.session.add_all([squat, push_up, plank, rowing, lunge])
    db.session.commit()

    print("Seeding workouts...")
    today = date.today()
    leg_day = Workout(
        date=today - timedelta(days=3),
        duration_minutes=60,
        notes='Heavy lower body session.'
    )
    conditioning = Workout(
        date=today - timedelta(days=1),
        duration_minutes=35,
        notes='Short conditioning circuit.'
    )
    core_day = Workout(
        date=today,
        duration_minutes=25,
        notes='Core and mobility only.'
    )

    db.session.add_all([leg_day, conditioning, core_day])
    db.session.commit()

    print("Seeding workout exercises...")
    db.session.add_all([
        WorkoutExercise(workout=leg_day, exercise=squat, sets=5, reps=5),
        WorkoutExercise(workout=leg_day, exercise=lunge, sets=3, reps=12),
        WorkoutExercise(workout=conditioning, exercise=rowing, duration_seconds=600),
        WorkoutExercise(workout=conditioning, exercise=push_up, sets=4, reps=15),
        WorkoutExercise(workout=core_day, exercise=plank, duration_seconds=90),
        WorkoutExercise(workout=core_day, exercise=lunge, sets=2, reps=10),
    ])
    db.session.commit()

    print("Done seeding.")
