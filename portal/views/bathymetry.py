from models.bathymetry import Bathymetry, BathymetryCoordinate
from models.site import Site
from flask_security import current_user
from views.general import UserModelView


class BathymetryView(UserModelView):
    column_list = (
        "site",
        Bathymetry.timestamp
    )
    form_columns = ("site", Bathymetry.timestamp)

    form_args = {
        "site": {
            "query_factory": lambda: Site.query.filter_by(
                user_id=current_user.id
            )
        }
    }
    column_labels = {
        "site": "Site name",
        "timestamp": "Time stamp",
    }

    column_descriptions = {
        "site": "Name of the site as provided in your site setup",
        "timestamp": "Time of measurement of the bathymetry cross section",
    }

    create_template = "bathymetry/create.html"
    edit_template = "bathymetry/edit.html"
    details_template = "bathymetry/details.html"


    # Don't show bathymetry for sites which are not from this user.
    def get_query(self):
        return super(BathymetryView, self).get_query().join(Site).filter_by(user_id=current_user.id)

    # Don't allow to access a specific movie if it's not from this user.
    def get_one(self, id):
        return super(BathymetryView, self).get_query().filter_by(id=id).join(Site).filter_by(user_id=current_user.id).one()

