import requests
import os

from flask_restx import Namespace, Resource, abort, fields, marshal_with
from flask_security import roles_accepted
from flask_login import current_user

api = Namespace("license", description="License related operations")

license_serializer = {
    "id": fields.String,
    "improviser_user": fields.String,
    "is_recurring": fields.Boolean,
    "seats": fields.Integer,
    "name": fields.String,
    "start_date": fields.String,
    "end_date": fields.String,
}


@api.route("/")
@api.doc("License operations")
class LicenseResource(Resource):
    @marshal_with(license_serializer)
    @roles_accepted("admin", "moderator", "member", "student", "teacher", "operator", "school")
    def get(self):
        """Get License"""

        baseurl = os.environ.get('API_URL') + os.environ.get('API_VERSION')

        headers = {'Content-Type': 'application/json'}

        r = requests.get(baseurl + '/licenses/improviser/' + str(current_user.id), headers=headers)

        license = r.json()

        return license, 200
