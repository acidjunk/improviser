import datetime
import uuid
import structlog
from apis.helpers import query_with_filters, get_range_from_args, get_sort_from_args, get_filter_from_args

from flask_login import current_user
from flask_security import roles_accepted
from musthe import Note, Interval
from security import quick_token_required

from flask_restx import Namespace, Resource, fields, marshal_with, reqparse, abort

from database import db, Riff, RiffExercise, RiffExerciseItem

from .riffs import riff_fields, riff_arguments

logger = structlog.get_logger(__name__)

api = Namespace("exercises", description="Exercise related operations")

annotation_fields = {
    "from": fields.Integer,
    "to": fields.Integer,
    "label": fields.String,
    "text": fields.String,
}

tag_info_marshaller = {
    "id": fields.String,
    "name": fields.String,
}

exercise_list_serializer = api.model(
    "RiffExercise",
    {
        "id": fields.String(required=True),
        "name": fields.String(required=True, description="Unique exercise name"),
        "description": fields.String(required=True, description="Description", default=False),
        "is_public": fields.Boolean(
            required=True, description="Is this riff exercise visible to everyone?", default=False
        ),
        "root_key": fields.String(
            required=True, description="Root key of exercise (for printing purposes in the future)", default=False
        ),
        "created_at": fields.DateTime(),
        "created_by": fields.String(),
        "modified_at": fields.DateTime(),
        "gravatar_image": fields.String(),
        "tags": fields.Nested(tag_info_marshaller),
        "stars": fields.Integer(),
        "instrument_key": fields.String(),
        "instruments": fields.List(fields.String),
    },
)

exercise_item_serializer = api.model(
    "RiffExerciseItem",
    {
        "riff_exercise_id": fields.String(required=True),
        "number_of_bars": fields.Integer(required=True),
        "pitch": fields.String(required=True),
        "octave": fields.Integer(required=True),
        "order_number": fields.Integer(required=True),
        "chord_info": fields.String(required=False),  # transposed riff chord info will be used
        "chord_info_alternate": fields.String(
            required=False
        ),  # this item is overriden with other chords (lilypond format)
        "chord_info_backing_track": fields.String(required=False),  # this item is overrides backing track chord info
        "riff_id": fields.String(required=True, description="The riff"),
        "created_at": fields.DateTime(),
    },
)

exercise_detail_serializer = api.model(
    "RiffExercise",
    {
        "id": fields.String(required=True),
        "name": fields.String(required=True, description="Unique exercise name"),
        "description": fields.String(required=True, description="Description", default=False),
        "is_public": fields.Boolean(
            required=True, description="Is this riff exercise visible to everyone?", default=False
        ),
        "root_key": fields.String(
            required=True, description="Root key of exercise (for printing purposes in the future)", default=False
        ),
        "created_at": fields.DateTime(),
        "created_by": fields.String(),
        "modified_at": fields.DateTime(),
        "gravatar_image": fields.String(),
        "tags": fields.Nested(tag_info_marshaller),
        "exercise_items": fields.Nested(exercise_item_serializer),
        "riffs": fields.Nested(riff_fields),
        "annotations": fields.Nested(annotation_fields),
        "tempo": fields.Integer(),
    },
)

exercise_item_fields = {
    "pitch": fields.String(required=True),
    "octave": fields.Integer(required=True),
    "order_number": fields.Integer(required=True),
    "riff_id": fields.String(required=True, description="The riff"),
    # Todo: determine if we ever need the chord_info in post/put (always loaded from DB?)
    # "chord_info": fields.String(required=False),
    "chord_info_alternate": fields.String(
        required=False, description="Overrule riff chord info (if any) with your own " "LilyPond riff info"
    ),
    "chord_info_backing_track": fields.String(
        required=False,
        description="Overrule riff chord info (if any) with your own "
        "LilyPond riff info to help the BackinTrack matcher",
    ),
    "use_alternate_chord_info_for_backing_track": fields.Boolean(required=False, default=True),
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

copy_exercise_fields = {"new_exercise_id": fields.String}

exercise_detail_fields = exercise_fields

exercise_arguments = reqparse.RequestParser()
exercise_arguments.add_argument(
    "search_phrase", type=str, required=False, help="Return only items that contain the search_phrase"
)

exercise_message_fields = {
    "available": fields.Boolean,
    "reason": fields.String,
}

quick_transpose_sub_fields = {
    "riff_id": fields.String,
    "pitch": fields.String(required=True),
}

quick_transpose_fields = {
    "riffs": fields.Nested(quick_transpose_sub_fields),
}

transpose_fields = {
    "riff_id": fields.String,  # optional
    "exercise_item_id": fields.String,  # optional
    "pitch": fields.String(required=True),
    "chord_info": fields.String(required=True),
    "chord_info_alternate": fields.String,
    "chord_info_backing_track": fields.String,
}


parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


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

    # *****************************************************************************************************************
    # Todo: expose via REST API -> so the client can use it to calculate the correct lilypond chord info values upon
    #  changing the pitch of an exercise item
    # *****************************************************************************************************************

    notes = {
        "c": "P1",
        "cis": "A1",
        "d": "M2",
        "ees": "m3",
        "e": "M3",
        "f": "P4",
        "fis": "A4",
        "g": "P5",
        "gis": "A5",
        "aes": "m6",
        "a": "M6",
        "bes": "m7",
        "b": "M7",
    }
    to_lilypond = {
        "db": "des",
        "eb": "ees",
        "ab": "aes",
        "bb": "bes",
        "c#": "cis",
        "d#": "dis",
        "e#": "f",
        "f#": "fis",
        "g#": "gis",
        "a#": "ais",
        "b#": "c",
    }
    lilypond_mood = {"M": "maj", "m": "m"}

    if chord_info and len(chord_info) and chord_info[0].isupper():
        if len(chord_info) > 1 and (chord_info[1] == "#" or chord_info[1] == "b"):
            root_key = str(Note(chord_info[0:2]) + Interval(notes[pitch])).lower()
            o = 1
        else:
            root_key = str(Note(chord_info[0]) + Interval(notes[pitch])).lower()
            o = 0
        if root_key in to_lilypond.keys():
            root_key = to_lilypond[root_key]
        # Done with root key : continue with rest of chord
        digit = ""
        separator = ":"
        if len(chord_info) == 1:
            chord_mood = ""
            separator = ""
        elif chord_info[1 + o].isdigit():  # Handle C7, C#7, Bb7
            chord_mood = ""
            digit = chord_info[1 + o]
        elif len(chord_info) == 2 + o:  # Handle Cm, C#m, Bbm, CM, C#M
            chord_mood = (
                lilypond_mood[chord_info[1 + o]] if chord_info[1 + o] in lilypond_mood.keys() else chord_info[1 + o]
            )
        elif len(chord_info) == 3 + o:  # Handle Cm7, C#m7, CM7, BbM9, Cm9, CM6
            chord_mood = (
                lilypond_mood[chord_info[1 + o]] if chord_info[1 + o] in lilypond_mood.keys() else chord_info[1 + o]
            )
            digit = chord_info[2 + o]
        elif len(chord_info) == 4 + o:  # Handle Cmaj
            chord_mood = chord_info[1 + o : 4 + o]
        elif len(chord_info) == 5 + o:  # Handle Cmaj7
            chord_mood = chord_info[1 + o : 4 + o]
            digit = chord_info[4 + o]
        else:
            logger.info("Couldn't parse chord info", chord_info=chord_info)
            raise ValueError
        logger.info("Using chord from riff", root_key=root_key, chord_mood=chord_mood, digit=digit)
        if not number_of_bars or number_of_bars == 1:
            return f"{root_key}1{separator}{chord_mood}{digit}"
        result = []
        for i in range(0, number_of_bars):
            result.append(f"{root_key}1{separator}{chord_mood}{digit}")
        return " ".join(result)
    elif chord_info:
        chords = chord_info.split(" ")
        logger.info("Using chord-info in lilypond format", chords=chords, pitch=pitch)
        result = []
        for chord in chords:
            if ":" in chord:
                root_key, chord_mood = chord.split(":")
                duration = root_key[1] if len(root_key) == 2 else ""
                root_key = str(Note(root_key[0].upper()) + Interval(notes[pitch])).lower()
                if root_key in to_lilypond.keys():
                    root_key = to_lilypond[root_key]
                root_key = root_key + duration
                result.append(f"{root_key}:{chord_mood}")
            else:
                logger.error("Expected ':' in chord", chord=chord, complete_chord_info=chord_info)
                result.append(f"Error in:{chord}")
        return " ".join(result)


@api.route("/validate-exercise-name/<string:name>")
class ValidateExerciseNameResource(Resource):
    @quick_token_required
    def get(self, name):
        exercise = (
            RiffExercise.query.filter(RiffExercise.name == name)
            .filter(RiffExercise.created_by == current_user.id)
            .first()
        )
        if not exercise:
            return {"available": True, "reason": ""}
        else:
            return {"available": False, "reason": "This exercise name already exists for the current user"}


@api.route("/")
class ExerciseResourceList(Resource):
    @roles_accepted("admin", "moderator", "member", "student", "teacher", "operator")
    @marshal_with(exercise_list_serializer)
    @api.expect(exercise_arguments)
    def get(self):
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args)
        filter = get_filter_from_args(args)

        # Get public exercises and exercises owned by this user
        exercise_query = RiffExercise.query.filter(
            (RiffExercise.created_by == current_user.id) | (RiffExercise.is_public.is_(True))
        )

        query_result, content_range = query_with_filters(
            RiffExercise, exercise_query, range, sort, filter, quick_search_columns=["name", "id"]
        )

        for exercise in query_result:
            exercise.tags = [{"id": tag.id, "name": tag.tag.name} for tag in exercise.riff_exercise_to_tags]

        return query_result, 200, {"Content-Range": content_range}

    @roles_accepted("admin", "moderator", "student", "teacher", "operator")
    @api.expect(exercise_fields)
    def post(self):
        exercise_items = api.payload.pop("exercise_items", [])

        validate_exercise_items_and_error(len(exercise_items))
        user_exercises = RiffExercise.query.filter(RiffExercise.created_by == current_user.id).all()
        if current_user.username != "acidjunk":
            validate_exercises_and_error(len(user_exercises))

        # Todo: add instruments selection and instrument key
        exercise = RiffExercise(**api.payload, created_by=str(current_user.id))
        exercise.modified_at = datetime.datetime.now()
        db.session.add(exercise)

        for exercise_item in exercise_items:
            # Try retrieving it from the riff itself
            riff = Riff.query.filter(Riff.id == exercise_item["riff_id"]).first()
            chord_info = riff.chord_info if riff.chord_info else riff.chord
            if chord_info:
                exercise_item["chord_info"] = transpose_chord_info(
                    chord_info, exercise_item["pitch"], riff.number_of_bars
                )
                logger.info(
                    "Using chord_info",
                    riff_id=riff.id,
                    riff_name=riff.name,
                    chord_info=chord_info,
                    transposed_chord_info=exercise_item["chord_info"],
                )
            else:
                logger.warning("Couldn't find any chord_info for riff", riff_id=riff.id, riff_name=riff.name)
            logger.info("Adding item to exercise", item=exercise_item, exercise_id=api.payload["id"])
            record = RiffExerciseItem(**exercise_item, id=str(uuid.uuid4()), riff_exercise_id=api.payload["id"], number_of_bars=riff.number_of_bars)
            db.session.add(record)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error("DB exercise add caused a rollback", error=error)
            abort(400, "DB error: {}".format(str(error)))
        return 201


@api.route("/<string:exercise_id>")
class ExerciseResource(Resource):
    @roles_accepted("admin", "moderator", "member", "student", "teacher", "operator")
    @marshal_with(exercise_detail_serializer)
    def get(self, exercise_id):
        try:
            exercise = (
                RiffExercise.query.filter(
                    (RiffExercise.created_by == current_user.id) | (RiffExercise.is_public.is_(True))
                )
                .filter(RiffExercise.id == exercise_id)
                .first()
            )
        except:
            abort(404, "exercise not found")
        exercise.tags = [str(tag.name) for tag in exercise.riff_exercise_tags]
        exercise.tags = [{"id": tag.id, "name": tag.tag.name} for tag in exercise.riff_exercise_to_tags]

        exercise.exercise_items = sorted(exercise.riff_exercise_items, key=lambda item: item.order_number)

        # Include riffs used in the exercise in the response
        riff_ids = [item.riff_id for item in exercise.exercise_items]
        exercise.riffs = Riff.query.filter(Riff.id.in_(riff_ids)).all()
        return exercise

    @roles_accepted("admin", "moderator", "student", "teacher", "operator")
    @api.expect(exercise_fields)
    def put(self, exercise_id):
        payload = api.payload
        exercise = RiffExercise.query.filter_by(id=exercise_id).first()
        exercise.modified_at = datetime.datetime.now()
        exercise.name = payload["name"]
        exercise.description = payload["description"]
        exercise.tempo = payload["tempo"]
        try:
            exercise.stars = payload["stars"]
        except:
            pass

        # prepare dicts for compare
        exercise_items = sorted(exercise.riff_exercise_items, key=lambda item: item.order_number)
        payload_exercise_items = sorted(payload["exercise_items"], key=lambda item: item["order_number"])

        validate_exercise_items_and_error(len(payload_exercise_items))

        changed = False

        for order_number, payload_exercise_item in enumerate(payload_exercise_items):
            if order_number >= len(exercise_items):
                logger.info("Inserting new exercise item", order_number=order_number, payload=payload_exercise_item)

                # Todo: remove double chord code in new/update
                riff = Riff.query.filter(Riff.id == payload_exercise_item["riff_id"]).first()

                if riff.chord_info:
                    # check transpose
                    tranposed_chord = transpose_chord_info(riff.chord_info, payload_exercise_item["pitch"], riff.number_of_bars)
                    payload_exercise_item["chord_info"] = tranposed_chord
                elif riff.chord:
                    # check transpose
                    tranposed_chord = transpose_chord_info(riff.chord, payload_exercise_item["pitch"], riff.number_of_bars)
                    payload_exercise_item["chord_info"] = tranposed_chord
                else:
                    logger.warning("riff doesn't contain chord info", id=riff.id, name=riff.name)
                    # correct faulty ones for now:
                    payload_exercise_item["chord_info"] = ""
                ################

                new_exercise_item = {**payload_exercise_item, "riff_exercise_id": exercise_id,  "number_of_bars": riff.number_of_bars,  "created_at": datetime.datetime.now(), "modified_at": datetime.datetime.now()}
                # Todo: remove double code in new/update
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

                # Todo: remove double chord code in new/update
                riff = Riff.query.filter_by(id=exercise_item_dict["riff_id"]).first()
                if riff.chord_info:
                    # check transpose
                    tranposed_chord = transpose_chord_info(riff.chord_info, payload_exercise_item["pitch"], riff.number_of_bars)
                    payload_exercise_item["chord_info"] = tranposed_chord
                elif riff.chord:
                    # check transpose
                    tranposed_chord = transpose_chord_info(riff.chord, payload_exercise_item["pitch"], riff.number_of_bars)
                    payload_exercise_item["chord_info"] = tranposed_chord
                else:
                    logger.warning("riff doesn't contain chord info", id=riff.id, name=riff.name)
                    # correct faulty ones for now:
                    payload_exercise_item["chord_info"] = ""
                ################

                added, removed, modified, same = dict_compare(exercise_item_dict, payload_exercise_item)
                logger.debug("Handling exercise item", added=added, removed=removed, modified=modified, same=same)
                if modified:
                    logger.info("Updating exercise item", order_number=order_number, payload=payload_exercise_item)
                    RiffExerciseItem.query.filter_by(id=exercise_item_dict["id"]).update(
                        {**payload_exercise_item, "number_of_bars": riff.number_of_bars, "modified_at": datetime.datetime.now()}
                    )
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
                abort(400, "DB error: {}".format(str(error)))
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
                logger.error("DB exercise item delete caused a rollback", error=error)
                abort(400, "DB error: {}".format(str(error)))
        return 204


def validate_exercise_items_and_error(items_length):
    if items_length > 99:
        message = "Exercise items constraint reached. Max 100 items for now."
        logger.error(message, items=items_length)
        abort(400, message)


def validate_exercises_and_error(items_length):
    if items_length > 10:
        message = "Exercise constraint reached. Max 10 exercises for free accounts. Contact me if you need more."
        logger.error(message, items=items_length)
        abort(400, message)


def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same


@api.route("/copy/<string:exercise_id>")
class CopyExerciseResource(Resource):
    @roles_accepted("admin", "moderator", "student", "teacher", "operator")
    @api.expect(exercise_fields)
    def post(self, exercise_id):
        exercise = RiffExercise.query.filter(RiffExercise.id == exercise_id).first()
        if exercise.created_by != current_user.id or (exercise.is_public and not exercise.is_copyable):
            logger.error(
                "Unable to copy exercise",
                user_id=str(current_user.id),
                created_by=str(exercise.created_by),
                public=exercise.is_public,
                copyable=exercise.is_copyable,
            )
            return abort(400, "Unable to copy exercise")

        # Query all exercises of this user that start with the old exercise name:
        exercise_name_check_query = (
            RiffExercise.query.filter(RiffExercise.created_by == current_user.id)
            .filter(RiffExercise.name.startswith(exercise.name))
            .order_by(RiffExercise.name)
            .all()
        )
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
                    name = " ".join(words[:-1]) + str(int(words[-1]) + 1)
                    logger.info("Generated name", exercise_name=exercise.name, name=name)
                else:
                    logger.info("Last name doesn't end on a digit: adding Variation 1")
                    name = f"{last_name} Variation 1"
            except:
                logger.error("Failed generating a name", exercise_name=exercise.name, taken=taken_exercise_names)
                return abort(400, "Failed generating a new name")

        record = RiffExercise(
            id=api.payload["new_exercise_id"],
            name=name,
            description=exercise.description,
            created_by=str(current_user.id),
            is_public=False,
            is_copyable=False,
            instrument_key=exercise.instrument_key,
            root_key=exercise.root_key,
        )
        db.session.add(record)

        # Copy exercise items
        for item in exercise.riff_exercise_items:
            record = RiffExerciseItem(
                id=str(uuid.uuid4()),
                riff_exercise_id=api.payload["new_exercise_id"],
                riff_id=item.riff_id,
                pitch=item.pitch,
                chord_info=item.chord_info,
                octave=item.octave,
                order_number=item.order_number,
            )
            db.session.add(record)

        try:
            db.session.commit()
            logger.info("Exercise copied successfully", id=exercise_id)
        except Exception as error:
            db.session.rollback()
            logger.error("DB exercise update caused a rollback", error=error)
            abort(400, "DB error: {}".format(str(error)))
        return 201


@api.route("/scales")
class ScaleTrainerResourceList(Resource):
    @marshal_with(riff_fields)
    @api.expect(riff_arguments)
    def get(self):
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args)
        filter = get_filter_from_args(args)

        riffs_query = Riff.query.filter(Riff.scale_trainer_enabled).filter(Riff.render_valid)

        query_result, content_range = query_with_filters(
            Riff, riffs_query, range, sort, filter, quick_search_columns=["name", "id"]
        )

        for riff in query_result:
            riff.tags = [{"id": tag.id, "name": tag.tag.name} for tag in riff.riff_to_tags]
            riff.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"
        return query_result, 200, {"Content-Range": content_range}


@api.route("/transpose-riff")
class Transpose(Resource):
    @api.expect(transpose_fields)
    def post(self):
        pitch = api.payload["pitch"]

        # If a riff_id is present the chord info from the DB wil be used.
        riff_id = api.payload.get("riff_id")
        if riff_id:
            riff = Riff.query.filter(Riff.id == riff_id).first()
            if riff.chord_info:
                chord_info = transpose_chord_info(riff.chord_info, pitch)
            else:
                chord_info = transpose_chord_info(riff.chord, pitch)
        else:
            if api.payload.get("chord_info"):
                chord_info = transpose_chord_info(api.payload["chord_info"], pitch)
            else:
                chord_info = ""

        # If a exercise_item_id is present the alternate_chord info from the DB wil be used.
        exercise_item_id = api.payload.get("exercise_item_id")
        chord_info_alternate = api.payload.get("chord_info_alternate")
        if chord_info_alternate:
            logger.info("Alternate chord info found in payload", chord_info_alternate=chord_info_alternate)
        if exercise_item_id and chord_info_alternate:
            exercise_item = RiffExerciseItem.query.filter(RiffExerciseItem.id == exercise_item_id).first()

            # only existing alternate chord info is transposed
            if exercise_item.chord_info_alternate:
                chord_info_alternate = "TODO"
                # chord_info_alternate = transpose_chord_info(riff.chord_info, pitch)

            logger.info("Alternate chord info transposed", chord_info_alternate=chord_info_alternate)

        chord_info_backing_track = api.payload.get("chord_info_backing_track")
        if chord_info_backing_track:
            logger.info("Backing track chord info found in payload", chord_info_backing_track=chord_info_backing_track)
        if exercise_item_id and chord_info_alternate:
            exercise_item = RiffExerciseItem.query.filter(RiffExerciseItem.id == exercise_item_id).first()

            # only existing alternate chord info is transposed
            if exercise_item.chord_info_backing_track:
                chord_info_backing_track = "TODO"
                # chord_info_alternate = transpose_chord_info(riff.chord_info, pitch)

            logger.info("Backing track chord info transposed", chord_info_backing_track=chord_info_backing_track)

        return {
            "chord_info": chord_info,
            "chord_info_alternate": chord_info_alternate,
            "chord_info_backing_track": chord_info_backing_track,
        }
