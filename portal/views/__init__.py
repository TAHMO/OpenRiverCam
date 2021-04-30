import flask_admin as admin
from flask_admin.base import AdminIndexView
# Models for CRUD views.
from models import db
from models.camera import CameraType, Camera, CameraConfig
from models.bathymetry import Bathymetry
from models.site import Site
from models.movie import Movie
from models.ratingcurve import RatingCurve

from views.camera import CameraConfigView, CameraTypeView, CameraView
from views.movie import MovieView
from views.movie import MovieView
from views.bathymetry import BathymetryView
from views.site import SiteView
from views.ratingcurve import RatingCurveView
from views.general import LogoutMenuLink, LoginMenuLink, UserModelView

from views.help import HelpView

admin = admin.Admin(name="OpenRiverCam", template_mode="bootstrap4", base_template="base.html",
                    index_view=AdminIndexView(url="/portal", menu_icon_type="fa", menu_icon_value="fa-home"))


# Login/logout menu links.
admin.add_link(LogoutMenuLink(name="Logout", category="", url="/logout", icon_type="fa",
                              icon_value="fa-user"))
admin.add_link(LoginMenuLink(name="Login", category="", url="/login", icon_type="fa",
                              icon_value="fa-user-o"))

# Specific Site view
admin.add_view(SiteView(Site, db, name="Sites", url="sites", category="Setup",
                        menu_icon_type="fa", menu_icon_value="fa-map-marker"
                        ))
admin.add_view(
    BathymetryView(Bathymetry, db, name="Bathymetry", url="bathymetry", category="Setup",
                   menu_icon_type="fa", menu_icon_value="fa-bar-chart"
                   )
)
admin.add_view(
    CameraTypeView(
        CameraType, db, name="Camera types", url="camera-types", category="Setup",
        menu_icon_type="fa", menu_icon_value="fa-camera"
    )
)
admin.add_view(
    CameraView(Camera, db, name="Cameras on sites", url="cameras", category="Setup",
               menu_icon_type="fa", menu_icon_value="fa-video-camera")
)
admin.add_view(
    CameraConfigView(
        CameraConfig,
        db,
        name="Camera configuration",
        url="camera-config",
        category="Setup",
        menu_icon_type="fa",
        menu_icon_value="fa-wrench"
    )
)

# Movie views.
admin.add_view(MovieView(Movie, db, name="Movies", url="movies", menu_icon_type="fa",
                         menu_icon_value="fa-film"))

# Custom user views.
admin.add_view(RatingCurveView(RatingCurve, db, name="Rating curves", url="ratingcurves",
                               menu_icon_type="fa", menu_icon_value="fa-line-chart"))

# Publicly visible pages.
admin.add_view(HelpView(name="Help", url="help", menu_icon_type="fa", menu_icon_value="fa-question-circle"))

