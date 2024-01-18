import requests
import json
import os

from flask_restx import Namespace, Resource, abort, fields, marshal_with
from flask_security import roles_accepted

from urllib.parse import quote

api = Namespace("table", description="Table related operations")


@api.route("/<email>")
@api.doc("Table operations")
class TableResource(Resource):
    @marshal_with({'table_id': fields.String(required=True)})
    @roles_accepted("admin", "moderator", "member", "student", "teacher", "operator", "school")
    def get(self, email):
        """Get Table"""

        baseurl = os.environ.get('API_URL') + os.environ.get('API_VERSION')

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {'username': os.environ.get('PRICELIST_USER'), 'password': os.environ.get('PRICELIST_PASSWORD')}
        r = requests.post(baseurl + '/login/access-token', data=body, headers=headers)
        token = r.json().get('access_token')

        headers = {'Authorization': 'Bearer ' + token}

        r = requests.get(baseurl + '/tables?filter=name%3A' + quote(email, encoding='utf-8') +
                         "&filter=shop_id%3Ac324e3f5-72ce-496f-a945-312cd493cf4c", headers=headers, data=None)

        table_id = ''

        if len(r.json()) == 0:
            body = {'name': email, 'shop_id': 'c324e3f5-72ce-496f-a945-312cd493cf4c'}
            r = requests.post(baseurl + '/tables', headers=headers, data=json.dumps(body))
            table_id = r.json().get('id')
        else:
            table_id = r.json()[0].get('id')

        response_data = {'table_id': table_id}
        return response_data, 200
