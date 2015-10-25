import os

from flask_assets import Bundle
from flask.ext.assets import Environment
from webassets.filter import register_filter

from webassets_babel import BabelFilter
from webassets_browserify import Browserify
from webassets_libsass import LibSass
from webassets_ng_annotate import NgAnnotateFilter

path, _ = os.path.split(__file__)

register_filter(NgAnnotateFilter)
register_filter(BabelFilter)
register_filter(Browserify)
register_filter(LibSass)

# not sure why but the debug false is required here
sass_app = Bundle("sass/main.scss", filters="libsass", output="css/main.css", debug=False)
# css_vendor = Bundle("vendor/node_modules/toastr/build/toastr.css")
css_all = Bundle(sass_app,
                 # css_vendor,
                 filters="cssmin", output="css/all.min.css")

js_bundle = Bundle("app.js",
                   filters=[
                       "babel",
                       "browserify",
                       "ng-annotate"
                   ],
                   output='bundle.js')

# ** not sure why minifying and the bundling in the same step
# ** doesn't cause the code to be minified
js_all = Bundle(js_bundle, filters="rjsmin", output="bundle.min.js")

webassets = Environment()

def init_app(app):
    webassets.app = app
    webassets.init_app(app)
    webassets.register('css_all', css_all)
    webassets.register('js_all', js_all)

    # ** always cache to speed up dev build time
    # webassets.manifest = 'cache' if not app.debug else False
    # webassets.cache = not app.debug
    webassets.cache = True
    webassets.debug = app.debug
    webassets.config['BROWSERIFY_EXTRA_ARGS'] = ['--extension=.es6']
    webassets.config['BROWSERIFY_TRANSFORMS'] = ['babelify', 'resolvify']
    webassets.config['LIBSASS_INCLUDES'] = [os.path.join(path, 'static/vendor/node_modules/bootstrap-sass/assets/stylesheets')]
