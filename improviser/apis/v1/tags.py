import uuid

import structlog
from apis.helpers import (
    get_filter_from_args,
    get_range_from_args,
    get_sort_from_args,
    load,
    query_with_filters,
    save,
    update,
)
from database import Tag
from flask_restplus import Namespace, Resource, fields, marshal_with
from flask_security import roles_accepted

logger = structlog.get_logger(__name__)

api = Namespace("tags", description="Tag related operations")

tag_serializer = api.model(
    "Tag", {"id": fields.String(), "name": fields.String(required=True, description="Unique tag name")}
)

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


@api.route("/")
@api.doc("Show all tags.")
class TagResourceList(Resource):
    @roles_accepted("admin")
    @marshal_with(tag_serializer)
    @api.doc(parser=parser)
    def get(self):
        """List Tags"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args)
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(Tag, Tag.query, range, sort, filter)
        return query_result, 200, {"Content-Range": content_range}

    @roles_accepted("admin")
    @api.expect(tag_serializer)
    @api.marshal_with(tag_serializer)
    def post(self):
        """New Shops"""
        tag = Tag(id=str(uuid.uuid4()), **api.payload)
        save(tag)
        return tag, 201


@api.route("/<id>")
@api.doc("Tag detail operations.")
class TagResource(Resource):
    @roles_accepted("admin")
    @marshal_with(tag_serializer)
    def get(self, id):
        """List Tag"""
        item = load(Tag, id)
        return item, 200

    @roles_accepted("admin")
    @api.expect(tag_serializer)
    @api.marshal_with(tag_serializer)
    def put(self, id):
        """Edit Tag"""
        item = load(Tag, id)
        item = update(item, api.payload)
        return item, 201
