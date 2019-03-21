import datetime
import uuid
import structlog

from flask_login import current_user
from flask_security import roles_accepted
from musthe import Note, Interval
from security import quick_token_required

from flask import request
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort

from database import db, Riff, RiffExercise, RiffExerciseItem
from sqlalchemy import cast, String

from .riffs import riff_fields

logger = structlog.get_logger(__name__)

api = Namespace("exercises", description="Exercise related operations")

annotation_fields = {
    "from": fields.Integer,
    "to": fields.Integer,
    "label": fields.String,
    "text": fields.String,
}

exercise_list_serializer = api.model("RiffExercise", {
    "id": fields.String(required=True),
    "name": fields.String(required=True, description="Unique exercise name"),
    "description": fields.String(required=True, description="Description", default=False),
    "is_public": fields.Boolean(required=True, description="Is this riff exercise visible to everyone?", default=False),
    "root_key": fields.String(required=True, description="Root key of exercise (for printing purposes in the future)", default=False),
    "created_at": fields.DateTime(),
    "created_by": fields.String(),
    "gravatar_image": fields.String(),
    "tags": fields.List(fields.String),
})

exercise_item_serializer = api.model("RiffExerciseItem", {
    "riff_exercise_id": fields.String(required=True, description="Unique exercise name"),
    "pitch": fields.String(required=True),
    "octave": fields.Integer(required=True),
    "order_number": fields.Integer(required=True),
    "chord_info": fields.String(required=False),  # when NOT provided; the chord info of the riffs will be used
    "riff_id": fields.String(required=True, description="The riff"),
    "created_at": fields.DateTime(),
})

exercise_detail_serializer = api.model("RiffExercise", {
    "name": fields.String(required=True, description="Unique exercise name"),
    "description": fields.String(required=True, description="Description", default=False),
    "is_public": fields.Boolean(required=True, description="Is this riff exercise visible to everyone?", default=False),
    "root_key": fields.String(required=True, description="Root key of exercise (for printing purposes in the future)", default=False),
    "created_at": fields.DateTime(),
    "created_by": fields.String(),
    "gravatar_image": fields.String(),
    "tags": fields.List(fields.String),
    "exercise_items": fields.Nested(exercise_item_serializer),
    "riffs": fields.Nested(riff_fields),
    "annotations": fields.Nested(annotation_fields),
    "tempo": fields.Integer()
})

exercise_item_fields = {
    "pitch": fields.String(required=True),
    "octave": fields.Integer(required=True),
    "order_number": fields.Integer(required=True),
    "riff_id": fields.String(required=True, description="The riff"),
    "chord_info": fields.String(required=False, description="Overrule riff chord info (if any) with your own "
                                                            "LilyPond riff info"),
}

exercise_fields = {
    "name": fields.String,
    "description": fields.String,
    "root_key": fields.String,
    "is_public": fields.Boolean,
    "created_at": fields.DateTime,
    "created_by": fields.String,
    "annotations": fields.Nested(annotation_fields),
    "exercise_items": fields.Nested(exercise_item_fields),
    "tempo": fields.Integer,
}

copy_exercise_fields = {
    "new_exercise_id": fields.String
}

exercise_detail_fields = exercise_fields
# exercise_detail_fields["riffs"] = fields.List(fields.Nested(riff_fields))


exercise_arguments = reqparse.RequestParser()
exercise_arguments.add_argument('search_phrase', type=str, required=False,
                                help='Return only items that contain the search_phrase')

exercise_message_fields = {
   'available': fields.Boolean,
   'reason': fields.String,
}


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def transpose_chord_info(chord_info, pitch, number_of_bars=None):
    """
    Transpose a chord_info string to lilypond chord info

    e.g.:
    chord_info: d2:m7 g:7 c1:maj7, with pitch: d => e2:m7 a:7 d1:maj7
    chord_info: C7, pitch: d, number_of_bars: 2 => d1:7 d1:7

    Note: when using C7 notation (from the riff.chord property) -> number of bars is mandatory

    return: new lilypond chord string
    """
    notes = {"c": "P1", "cis": "m1", "d": "M2", "ees": "m3", "e": "M3", "f": "P4", "fis": "A4", "g": "P5", "gis": "A5",
             "a": "M6", "bes": "m7", "b": "M7"}

    if chord_info[0].isupper():
        root_key = str(Note(chord_info[0]) + Interval(notes[pitch])).lower()
        chord_mood = root_key[1:] if len(root_key) > 1 else ""
        logger.info("Using chord from riff", root_key=root_key, chord_mood=chord_mood)
        # todo: add suff (e.g. maj9) when avail
        if not number_of_bars or number_of_bars == 1:
            return f"{root_key}{chord_mood}:1"
        return f"{root_key}{chord_mood}:1"
        # return " ".join([f"{root_key}{chord_mood}:1"] for i in range(number_of_bars))
    else:
        chords = chord_info.split(" ")
        logger.info("Using chord-info in lilypond format", chords=chords, pitch=pitch)
        result = []
        for chord in chords:
            if ":" in chord:
                root_key, chord_mood = chord.split(":")
                duration = root_key[1] if len(root_key) == 2 else ""
                root_key = str(Note(root_key[0].upper()) + Interval(notes[pitch])).lower() + duration
                result.append(f"{root_key}:{chord_mood}")
            else:
                logger.error("Expected and : in chord", chord=chord)
                result.append(f"Error in:{chord}")
        return " ".join(result)


@api.route('/validate-exercise-name/<string:name>')
class ValidateExerciseNameResource(Resource):

    @quick_token_required
    def get(self, name):
        exercise = RiffExercise.query.filter(RiffExercise.name == name)\
            .filter(RiffExercise.created_by == current_user.id).first()
        if not exercise:
            return {'available': True, 'reason': ''}
        else:
            return {'available': False, 'reason': 'This exercise name already exists for the current user'}


@api.route('/')
class ExerciseResourceList(Resource):

    @marshal_with(exercise_list_serializer)
    @api.expect(exercise_arguments)
    def get(self):
        args = request.args
        # Get public exercises and exercises owned by this user
        exercise_query = RiffExercise.query.filter((RiffExercise.created_by == current_user.id) |
                                                   (RiffExercise.is_public.is_(True)))
        if args.get("search_phrase"):
            # Handle case insensitive search
            exercise_query = exercise_query.filter(RiffExercise.name.ilike('%' + args["search_phrase"] + '%'))

        exercises = exercise_query.all()

        for exercise in exercises:
            exercise.tags = [str(tag.name) for tag in exercise.riff_exercise_tags]

        return exercises

    @quick_token_required
    @roles_accepted('admin', 'moderator', 'student', 'teacher', 'operator')
    @api.expect(exercise_fields)
    def post(self):
        exercise_items = api.payload.pop("exercise_items", [])
        exercise = RiffExercise(**api.payload, created_by=current_user.id)
        db.session.add(exercise)
        for exercise_item in exercise_items:
            chord_info = exercise_item.get("chord_info")
            if not chord_info:
                # Try retrieving it from the riff itself
                riff = Riff.query.filter(Riff.id == exercise_item["riff_id"]).first()
                chord_info = riff.chord_info if riff.chord_info else riff.chord
                if chord_info:
                    logger.info("Using chord_info", riff_id=riff.id, riff_name=riff.name, chord_info=chord_info)
                    exercise_item["chord_info"] = transpose_chord_info(chord_info, exercise_item["pitch"], riff.number_of_bars)
                else:
                    logger.warning("Couldn't find any chord_info for riff", riff_id=riff.id, riff_name=riff.name)
            else:
                # Todo: validate `user input` stuff
                # For now: just use it, and consider it transposed already -> plain simple store it
                pass

            logger.info("Adding item to exercise", item=exercise_item, exercise_id=api.payload['id'])
            record = RiffExerciseItem(**exercise_item, id=str(uuid.uuid4()), riff_exercise_id=api.payload["id"],
                                      created_by=str(current_user.id))
            db.session.add(record)

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error("DB exercise add caused a rollback", error=error)
            abort(400, 'DB error: {}'.format(str(error)))
        return 201


@api.route('/<string:exercise_id>')
class ExerciseResource(Resource):

    @marshal_with(exercise_detail_serializer)
    def get(self, exercise_id):
        exercise = RiffExercise.query. \
            filter((RiffExercise.created_by == current_user.id) | (RiffExercise.is_public.is_(True))).\
            filter(RiffExercise.id == exercise_id).first()
        exercise.tags = [str(tag.name) for tag in exercise.riff_exercise_tags]

        exercise.exercise_items = sorted(exercise.riff_exercise_items, key=lambda item: item.order_number)

        # Include riffs used in the exercise in the response
        riff_ids = [item.riff_id for item in exercise.exercise_items]
        exercise.riffs = Riff.query.filter(Riff.id.in_(riff_ids)).all()
        return exercise

    @quick_token_required
    @roles_accepted('admin', 'moderator', 'student', 'teacher', 'operator')
    @api.expect(exercise_fields)
    def put(self, exercise_id):
        payload = api.payload
        exercise = RiffExercise.query.filter_by(id=exercise_id).first()
        exercise.modified_at = datetime.datetime.now()
        exercise.name = payload["name"]

        exercise_items = sorted(exercise.riff_exercise_items, key=lambda item: item.order_number)
        payload_exercise_items = sorted(payload["exercise_items"], key=lambda item: item["order_number"])

        changed = False

        for order_number, payload_exercise_item in enumerate(payload_exercise_items):
            # prepare dicts for compare
            if order_number >= len(exercise_items):
                logger.info("Inserting new exercise item", order_number=order_number, payload=payload_exercise_item)
                new_exercise_item = {**payload_exercise_item, "riff_exercise_id": exercise_id}
                new_item = RiffExerciseItem(**new_exercise_item)
                db.session.add(new_item)
                changed = True
            else:
                exercise_item_dict = row2dict(exercise_items[order_number])
                payload_exercise_item["id"] = exercise_item_dict["id"]
                payload_exercise_item["order_number"] = str(payload_exercise_item["order_number"])
                payload_exercise_item["octave"] = str(payload_exercise_item["octave"])
                del exercise_item_dict["number_of_bars"]
                del exercise_item_dict["created_at"]
                del exercise_item_dict["modified_at"]
                added, removed, modified, same = dict_compare(exercise_item_dict, payload_exercise_item)
                logger.debug("Handling exercise item", added=added, removed=removed, modified=modified, same=same)
                if modified:
                    logger.info("Updating exercise item", order_number=order_number, payload=payload_exercise_item)
                    RiffExerciseItem.query.filter_by(id=exercise_item_dict["id"]).\
                        update({**payload_exercise_item, "modified_at": datetime.datetime.now()})
                    changed = True
                else:
                    logger.debug("Skipping update for", order_number=order_number)

        if changed:
            try:
                db.session.commit()
                logger.info("Exercise edit/insert successfully", id=exercise_id)
            except Exception as error:
                db.session.rollback()
                logger.error("DB exercise update caused a rollback", error=error)
                abort(400, 'DB error: {}'.format(str(error)))
            # refresh exercise from DB
            exercise = RiffExercise.query.filter_by(id=exercise_id).first()
            exercise_items = sorted(exercise.riff_exercise_items, key=lambda item: item.order_number)

        deleted = False

        for order_number, exercise_item in enumerate(exercise_items):
            if order_number >= len(payload_exercise_items):
                db.session.delete(exercise_item)
                deleted = True

        if deleted:
            try:
                db.session.commit()
                logger.info("Exercise item delete successfully", id=exercise_id)
            except Exception as error:
                db.session.rollback()
                logger.error("DB exercise update caused a rollback", error=error)
                abort(400, 'DB error: {}'.format(str(error)))
        return 204


def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same


@api.route('/copy/<string:exercise_id>')
class CopyExerciseResource(Resource):

    @quick_token_required
    @roles_accepted('admin', 'moderator', 'student', 'teacher', 'operator')
    @api.expect(exercise_fields)
    def post(self, exercise_id):
        exercise = RiffExercise.query.filter(RiffExercise.id == exercise_id).first()
        if exercise.created_by != current_user.id or (exercise.is_public and not exercise.is_copyable):
            logger.error("Unable to copy exercise", user_id=str(current_user.id), created_by=str(exercise.created_by),
                         public=exercise.is_public, copyable=exercise.is_copyable)
            return abort(400, "Unable to copy exercise")

        # Query all exercises of this user that start with the old exercise name:
        exercise_name_check_query = RiffExercise.query.\
            filter(RiffExercise.created_by == current_user.id).\
            filter(RiffExercise.name.startswith(exercise.name)).\
            order_by(RiffExercise.name).all()
        taken_exercise_names = [item.name for item in exercise_name_check_query]
        # Start with a name, when a user copies this from a public exercise the name will be free
        if not taken_exercise_names:
            name = exercise.name
        elif len(taken_exercise_names) == 1:
            name = f"{exercise.name} Variation 1"
        else:
            # Take last list item and add one
            last_name = taken_exercise_names[-1]
            logger.info("Trying to get a new name for name", name=last_name, taken=taken_exercise_names)
            try:
                words = last_name.split(" ")
                if words[-1].isdigit():
                    name = " ".join(words[:-1]) + str(int(words[-1])+1)
                    logger.info("Generated name", exercise_name=exercise.name, name=name)
                else:
                    logger.info("Last name doesn't end on a digit: adding Variation 1")
                    name = f"{last_name} Variation 1"
            except:
                logger.error("Failed generating a name", exercise_name=exercise.name, taken=taken_exercise_names)
                return abort(400, "Failed generating a new name")

        record = RiffExercise(id=api.payload["new_exercise_id"], name=name, description=exercise.description,
                              created_by=str(current_user.id), is_public=False, is_copyable=False,
                              instrument_key=exercise.instrument_key, root_key=exercise.root_key)
        db.session.add(record)

        # Copy exercise items
        for item in exercise.riff_exercise_items:
            record = RiffExerciseItem(id=str(uuid.uuid4()), riff_exercise_id=api.payload["new_exercise_id"],
                                      riff_id=item.riff_id, pitch=item.pitch, chord_info=item.chord_info,
                                      octave=item.octave, order_number=item.order_number)
            db.session.add(record)

        try:
            db.session.commit()
            logger.info("Exercise copied successfully", id=exercise_id)
        except Exception as error:
            db.session.rollback()
            logger.error("DB exercise update caused a rollback", error=error)
            abort(400, 'DB error: {}'.format(str(error)))
        return 201


@api.route('/scales')
class ScaleTrainerResourceList(Resource):

    @marshal_with(riff_fields)
    def get(self):
        riffs = Riff.query.filter(Riff.scale_trainer_enabled).all()
        return riffs
