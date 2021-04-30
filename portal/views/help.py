from flask import redirect
import flask_admin as admin


class HelpView(admin.BaseView):
    @admin.expose("/")
    def index(self):
        return redirect("https://openrivercam.readthedocs.io")
