from itertools import chain
from pathlib import Path
import os

from flask.ext.assets import Bundle, Environment
from webassets.filter import register_filter

from webassets_babel import BabelFilter
from webassets_browserify import Browserify
from webassets_libsass import LibSass

path, _ = os.path.split(__file__)

register_filter(BabelFilter)
register_filter(Browserify)
register_filter(LibSass)

# not sure why but the debug false is required here
sass_app = Bundle("sass/main.scss", filters="libsass", debug=False, output='dist/main.css')
# css_vendor = Bundle("vendor/node_modules/toastr/build/toastr.css")
css_all = Bundle(sass_app,
                 # css_vendor,
                 filters="cssmin", output="dist/all.min.css")

find_files = lambda p, g: (str(p.relative_to('bauble/static')) for p in Path(p).glob(g))

js_bundle = Bundle("app.js",
                   depends='*.js',
                   # depends=find_files('bauble/static', '**/*.js'),
                   # depends=chain(find_files('bauble/static/components', '**/*.js'),
                   #               find_files('bauble/static/shared', '**/*.js')),
                   filters=[
                       "babel",
                       "browserify",
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

    webassets.manifest = 'cache' if not app.debug else False
    webassets.cache = not app.debug
    webassets.debug = app.debug
    webassets.config['BROWSERIFY_EXTRA_ARGS'] = ['--extension=.es6']
    webassets.config['BROWSERIFY_TRANSFORMS'] = ['babelify', 'resolvify']
    webassets.config['LIBSASS_INCLUDES'] = [os.path.join(path, 'static/vendor/node_modules/bootstrap-sass/assets/stylesheets')]
