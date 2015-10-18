from flask_assets import Bundle
from flask.ext.assets import Environment
from webassets.filter import register_filter
from webassets_libsass import LibSass

register_filter(LibSass)

#: application css bundle
css_app = Bundle("sass/main.scss", filters="libsass", output="css/main.css",
                 debug=False)

css_menu = Bundle("sass/menu.scss", filters="libsass", output="css/menu.css",
                  debug=False)

#: consolidated css bundle
css_all = Bundle(# "css/bootstrap.min.css",
                 css_app,
                 # "css/bootstrap-responsive.min.css",
                 filters="cssmin", output="css/all.min.css")

#: vendor js bundletouc
# js_vendor = Bundle("js/vendor/jquery-1.10.1.min.js",
#                    "js/vendor/bootstrap-2.3.3.min.js",
#                    "js/vendor/underscore-1.4.4.min.js",
#                    "js/vendor/backbone-1.0.0.min.js",
#                    filters="rjsmin", output="js/vendor.min.js")

#: application js bundle
js_main = Bundle("js/*.js", filters="rjsmin", output="js/main.js")


webassets = Environment()

def init_app(app):
    webassets.app = app
    webassets.init_app(app)
    webassets.register('css_all', css_all)
    webassets.register('css_menu', css_menu)
    webassets.register('js_main', js_main)
    webassets.manifest = 'cache' if not app.debug else False
    webassets.cache = not app.debug
    webassets.debug = app.debug
