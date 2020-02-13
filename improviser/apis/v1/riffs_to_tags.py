import uuid

from apis.helpers import (
    get_range_from_args, get_sort_from_args, load, query_with_filters, save, update,
    get_filter_from_args
)
from database import Riff, RiffTag, Tag
from flask_restplus import Namespace, Resource, abort, fields, marshal_with
from flask_security import roles_accepted

api = Namespace("riffs-to-tags", description="Riff to tag related operations")

riff_to_tag_serializer = api.model(
    "RiffToTag",
    {
        "id": fields.String(),
        "tag_id": fields.String(required=True, description="Tag Id"),
        "riff_id": fields.String(required=True, description="Riff Id"),
    },
)

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


@api.route("/")
@api.doc("Create tags")
class RiffsToTagsResourceList(Resource):
    @marshal_with(riff_to_tag_serializer)
    @api.doc(parser=parser)
    def get(self):
        """List tags for a riff"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args, "id")
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(RiffTag, RiffTag.query, range, sort, filter)
        return query_result, 200, {"Content-Range": content_range}

    @roles_accepted("admin")
    @api.expect(riff_to_tag_serializer)
    @api.marshal_with(riff_to_tag_serializer)
    def post(self):
        """New RiffToTag"""
        tag = Tag.query.filter(Tag.id == api.payload["tag_id"]).first()
        riff = Riff.query.filter(Riff.id == api.payload["riff_id"]).first()

        if not tag or not riff:
            abort(400, "Tag or riff not found")

        check_query = RiffTag.query.filter_by(riff_id=riff.id).filter_by(tag_id=tag.id).all()
        if len(check_query) > 0:
            abort(409, "Relation already exists")

        riff_to_tag = RiffTag(id=str(uuid.uuid4()), riff=riff, tag=tag)
        save(riff_to_tag)

        return riff_to_tag, 201


@api.route("/<id>")
@api.doc("RiffToTag detail operations.")
class RiffsToTagsResource(Resource):
    @roles_accepted("admin")
    @marshal_with(riff_to_tag_serializer)
    def get(self, id):
        """List RiffToTag"""
        item = load(RiffTag, id)
        return item, 200

    @roles_accepted("admin")
    @api.expect(riff_to_tag_serializer)
    @api.marshal_with(riff_to_tag_serializer)
    def put(self, id):
        """Edit RiffToTag"""
        item = load(RiffTag, id)
        item = update(item, api.payload)
        return item, 201
