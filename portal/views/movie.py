from flask import flash, url_for, redirect
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_admin import expose
from flask_admin.actions import action
from flask_security import current_user
from models import db
from models.movie import Movie, MovieType
from models.site import Site
from models.camera import CameraConfig, Camera
from models.ratingcurve import RatingCurve, RatingPoint
from controllers import optimize_rating
from views.general import UserModelView
from views.elements.s3uploadfield import s3UploadField


class FilterMovieBySite(BaseSQLAFilter):
    # Override to create an appropriate query and apply a filter to said query with the passed value from the filter UI
    def apply(self, query, value, alias=None):
        return (
            query
                .filter(Site.id == value)
                .filter(Site.user_id == current_user.id)
        )

    # readable operation name. This appears in the middle filter line drop-down
    def operation(self):
        return u"equals"

    # Override to provide the options for the filter - in this case it's a list of the titles of the Client model
    def get_options(self, view):
        return [(site.id, site.name) for site in (Site.query.filter_by(user_id=current_user.id).order_by(Site.name) if current_user else [])]

class MovieView(UserModelView):
    column_list = (
        "config.camera.site",
        Movie.file_name,
        Movie.timestamp,
        Movie.actual_water_level,
        Movie.discharge_q50,
        Movie.status,
    )


    column_descriptions = {
        "timestamp": "User selected time stamp of movie",
        "discharge_q50": "Discharge based on frame-to-frame median velocities",
        "actual_water_level": "Water level as measured on staff gauge in view",
        "status": "Status indicator on level of processing performed",
    }

    column_labels = {"config.camera.site": "Site",
                     "timestamp": "Time stamp",
                     "actual_water_level": "Water level [m]",
                     "discharge_q50": "Median discharge [m3/s]",
                     "status": "Movie status",
                     }
    column_filters = [FilterMovieBySite(column=None, name="Site")]
    column_formatters = dict(
        discharge_q05=lambda v, c, m, p: "{:.3f}".format(m.discharge_q05)
        if m.discharge_q05
        else "",
        discharge_q25=lambda v, c, m, p: "{:.3f}".format(m.discharge_q25)
        if m.discharge_q25
        else "",
        discharge_q50=lambda v, c, m, p: "{:.3f}".format(m.discharge_q50)
        if m.discharge_q50
        else "",
        discharge_q75=lambda v, c, m, p: "{:.3f}".format(m.discharge_q75)
        if m.discharge_q75
        else "",
        discharge_q95=lambda v, c, m, p: "{:.3f}".format(m.discharge_q95)
        if m.discharge_q95
        else "",
    )

    form_columns = ("config", Movie.timestamp, "file_name", Movie.actual_water_level)
    form_extra_fields = {
        "file_name": s3UploadField(
            "File", allowed_extensions=("mkv", "mpeg", "mp4")
        )
    }
    form_args = {
        "config": {
            "query_factory": lambda: CameraConfig.query.join(Camera).join(Site).filter_by(
                user_id=current_user.id
            )
        }
    }
    form_create_rules = ("config", "timestamp", "file_name")

    create_template = "movie/create.html"
    edit_template = "movie/edit.html"
    form_edit_rules = ("timestamp", "actual_water_level")

    details_template = "movie/details.html"
    column_details_list = (
        "config",
        "timestamp",
        "file_name",
        "status",
        "actual_water_level",
        "discharge_q50",
    )

    # Don't show movies which are uploaded specifically for the camera config or movies not from this user.
    def get_query(self):
        return super(MovieView, self).get_query().filter_by(type=MovieType.MOVIE_TYPE_NORMAL).join(CameraConfig).join(Camera).join(Site).filter_by(user_id=current_user.id)

    # Don't allow to access a specific movie if it's not from this user.
    def get_one(self, id):
        return super(MovieView, self).get_query().filter_by(id=id).join(CameraConfig).join(Camera).join(Site).filter_by(user_id=current_user.id).one()

    # Need this so the filter options are always up-to-date.
    @expose("/")
    def index_view(self):
        self._refresh_filters_cache()
        return super(MovieView, self).index_view()

    @action('create_ratingcurve', 'Make rating curve')
    def action_create_ratingcurve(self, ids):
        movies = Movie.query.filter(Movie.id.in_(ids)).all()
        site_id = movies[0].config.camera.site_id
        print("#\n#\n#\n#\n#\n#\n#\n#\n#\n#\n#\n")

        # put together a dict of water levels and discharges, remove points that are not completed yet
        for movie in movies:
            valid_ids = [movie.id for movie in movies if (movie.actual_water_level and movie.discharge_q50)]
            rating_points  = dict(
                h=[movie.actual_water_level for movie in movies if (movie.actual_water_level and movie.discharge_q50)],
                Q=[movie.discharge_q50 for movie in movies if (movie.actual_water_level and movie.discharge_q50)],
            )
        print(rating_points)
        # fit rating curve and add curve and points to database
        if len(rating_points["h"]) > 4:
            # get the rating curve
            params = optimize_rating(**rating_points)
            # put parameters into rating table
            rating_curve = RatingCurve(site_id=site_id, **params)
            db.add(rating_curve)
            db.commit()
            db.refresh(rating_curve)
            # make individual rating points
            valid_movies = Movie.query.filter(Movie.id.in_(valid_ids)).all()
            for movie in valid_movies:
                rating_point = RatingPoint(
                    ratingcurve_id=rating_curve.id,
                    movie_id = movie.id,
                )
                db.add(rating_point)
            db.commit()
            db.refresh(rating_curve)
            flash(f"Rating curve with ID {rating_curve.id} stored")
            return redirect(url_for('ratingcurve.edit_view', id=rating_curve.id))

        else:
            flash("There are not enough rating points. Minimum 5 points are required to construct a rating curve")


