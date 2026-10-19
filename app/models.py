from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from datetime import datetime, timezone, date

db = SQLAlchemy()


class Workout(db.Model):
    __tablename__ = 'workouts'
    __table_args__ = (
        CheckConstraint('duration_minutes IS NULL OR duration_minutes > 0', name='ck_workout_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    duration_minutes = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workout_exercises = db.relationship('WorkoutExercise', back_populates='workout', cascade='all, delete-orphan')

    @property
    def exercises(self):
        return self.workout_exercises

    def validate_date(self):
        if self.date is None:
            raise ValueError("Workout date must be provided.")

    def validate_duration(self):
        if self.duration_minutes is not None and self.duration_minutes <= 0:
            raise ValueError("Workout duration_minutes must be a positive integer.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_date()
        self.validate_duration()

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "duration_minutes": self.duration_minutes,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "exercises": [we.to_dict() for we in self.workout_exercises]
        }


class Exercise(db.Model):
    __tablename__ = 'exercises'
    __table_args__ = (
        UniqueConstraint('name', name='uq_exercise_name'),
        CheckConstraint('LENGTH(name) > 0', name='ck_exercise_name_not_empty'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=True)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workout_exercises = db.relationship('WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan')

    def validate_name(self):
        if not self.name or not self.name.strip():
            raise ValueError("Exercise name must not be empty.")
        if len(self.name) > 100:
            raise ValueError("Exercise name must be 100 characters or fewer.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_name()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "equipment_needed": self.equipment_needed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    __table_args__ = (
        CheckConstraint('sets IS NULL OR sets > 0', name='ck_sets_positive'),
        CheckConstraint('reps IS NULL OR reps > 0', name='ck_reps_positive'),
        CheckConstraint('duration_seconds IS NULL OR duration_seconds > 0', name='ck_duration_seconds_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    def validate_metrics(self):
        if self.sets is None and self.reps is None and self.duration_seconds is None:
            raise ValueError("At least one metric (sets, reps, or duration_seconds) must be provided for a workout exercise.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_metrics()

    def to_dict(self):
        return {
            "id": self.id,
            "workout_id": self.workout_id,
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise.name if self.exercise else None,
            "sets": self.sets,
            "reps": self.reps,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
