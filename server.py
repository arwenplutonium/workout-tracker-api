from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import app
from app.models import db, Workout, Exercise, WorkoutExercise
from app.schemas import (
    workout_schema,
    exercise_schema,
    workout_exercise_schema,
)


# Workouts

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify([workout.to_dict() for workout in workouts]), 200


@app.route('/workouts/<int:workout_id>', methods=['GET'])
def get_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    return jsonify(workout.to_dict()), 200


@app.route('/workouts', methods=['POST'])
def create_workout():
    try:
        data = workout_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({"errors": [str(err)]}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": ["Workout violates a database constraint."]}), 400

    return jsonify(workout.to_dict()), 201


@app.route('/workouts/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    # The cascade on workout_exercises removes the join rows as well.
    db.session.delete(workout)
    db.session.commit()
    return "", 204


# Exercises

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify([exercise.to_dict() for exercise in exercises]), 200


@app.route('/exercises/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    return jsonify(exercise.to_dict()), 200


@app.route('/exercises', methods=['POST'])
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        exercise = Exercise(**data)
        db.session.add(exercise)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({"errors": [str(err)]}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": ["An exercise with that name already exists."]}), 400

    return jsonify(exercise.to_dict()), 201


@app.route('/exercises/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    db.session.delete(exercise)
    db.session.commit()
    return "", 204


# Workout exercises

def add_exercise(workout_id, payload):
    """Attach an exercise to a workout and return the updated workout."""
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    try:
        data = workout_exercise_schema.load(payload)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    exercise = db.session.get(Exercise, data['exercise_id'])
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    try:
        workout_exercise = WorkoutExercise(workout_id=workout.id, **data)
        db.session.add(workout_exercise)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({"errors": [str(err)]}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": ["Workout exercise violates a database constraint."]}), 400

    return jsonify(workout.to_dict()), 201


@app.route('/workouts/<int:workout_id>/exercises', methods=['POST'])
def add_exercise_to_workout(workout_id):
    return add_exercise(workout_id, request.get_json(silent=True) or {})


@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST']
)
def add_workout_exercise(workout_id, exercise_id):
    # Same action as above, with the exercise taken from the URL instead of the body.
    payload = dict(request.get_json(silent=True) or {})
    payload['exercise_id'] = exercise_id
    return add_exercise(workout_id, payload)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
