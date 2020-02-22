import uuid
from datetime import datetime

import structlog
from apis.helpers import save
from database import RecentRiffExercise, db
from flask_login import current_user
from flask_restplus import Namespace, Resource, fields, marshal_with
from flask_security import roles_accepted
from sqlalchemy import desc

logger = structlog.get_logger(__name__)

api = Namespace("recent-exercises", description="Recent Exercise related operations")

recent_exercise_serializer = api.model(
    "RecentExercise", {"riff_exercise_id": fields.String(required=True, description="Exercise Id"),}
)
recent_exercise_fields = {
    "id": fields.String,
    "riff_exercise_id": fields.String,
    "riff_exercise_name": fields.String,
}


@api.route("/")
@api.doc("Show all recent_exercises.")
class RecentExerciseResourceList(Resource):
    @roles_accepted("admin", "student")
    @marshal_with(recent_exercise_fields)
    def get(self):
        """List RecentExercises"""
        query_result = (
            RecentRiffExercise.query.filter(RecentRiffExercise.created_by == current_user.id)
            .order_by(desc(RecentRiffExercise.modified_at))
            .all()
        )
        return query_result, 200

    @roles_accepted("admin", "student")
    @api.expect(recent_exercise_serializer)
    @api.marshal_with(recent_exercise_serializer)
    def post(self):
        riff_exercise_id = api.payload["riff_exercise_id"]
        """New Recent Exercise"""
        # check if current one already exists in the list
        query_result = (
            RecentRiffExercise.query.filter(RecentRiffExercise.created_by == current_user.id)
            .filter(RecentRiffExercise.riff_exercise_id == riff_exercise_id)
            .all()
        )
        if len(query_result) == 0:
            logger.info("adding recent exercise", riff_exercise_id=riff_exercise_id, user_id=current_user.id)
            riff = RecentRiffExercise(
                id=str(uuid.uuid4()), riff_exercise_id=riff_exercise_id, created_by=current_user.id
            )
            save(riff)

            # clean to ensure max recent exerciss count is 5
            logger.info("cleaning recent exercises", user_id=current_user.id)
            query_result = (
                RecentRiffExercise.query.filter(RecentRiffExercise.created_by == current_user.id)
                .order_by(desc(RecentRiffExercise.modified_at))
                .offset(5)
            )
            [db.session.delete(i) for i in query_result]

            return riff, 201
        elif len(query_result) == 1:
            logger.info("updating recent exercise", riff_exercise_id=riff_exercise_id, user_id=current_user.id)
            riff = query_result[0]
            riff.modified_at = datetime.now()
            save(riff)
            return riff, 201
        logger.error("DB integrity problem for", riff_exercise_id=riff_exercise_id, user_id=current_user.id)
        return None, 500
