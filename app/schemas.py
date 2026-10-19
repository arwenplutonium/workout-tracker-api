from marshmallow import Schema, fields, validate, ValidationError, pre_load


def validate_not_empty(value):
    if not value or not value.strip():
        raise ValidationError("Field must not be empty.")


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(required=True)
    exercise_name = fields.String(dump_only=True)
    sets = fields.Integer(
        validate=validate.Range(min=1, error="Sets must be a positive integer."),
        allow_none=True
    )
    reps = fields.Integer(
        validate=validate.Range(min=1, error="Reps must be a positive integer."),
        allow_none=True
    )
    duration_seconds = fields.Integer(
        validate=validate.Range(min=1, error="Duration seconds must be a positive integer."),
        allow_none=True
    )
    created_at = fields.DateTime(dump_only=True)

    @pre_load
    def validate_at_least_one_metric(self, data, **kwargs):
        sets = data.get('sets')
        reps = data.get('reps')
        duration_seconds = data.get('duration_seconds')
        if sets is None and reps is None and duration_seconds is None:
            raise ValidationError(
                "At least one metric (sets, reps, or duration_seconds) must be provided.",
                field_name="sets"
            )
        return data


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=100, error="Exercise name must be between 1 and 100 characters."),
            validate_not_empty
        ]
    )
    category = fields.String(
        validate=validate.Length(max=50, error="Category must be 50 characters or fewer."),
        allow_none=True
    )
    equipment_needed = fields.Boolean(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(
        validate=validate.Range(min=1, error="Workout duration_minutes must be a positive integer."),
        allow_none=True
    )
    notes = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)


workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)
