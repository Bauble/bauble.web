import os
from importlib import import_module

from flask import Blueprint

root_path, _ = os.path.split(__file__)

class API(Blueprint):
    def register(self, *args, **kwargs):
        for controller in ['search', 'family', 'genus', 'taxon', 'accession', 'geography']:
            import_module('bauble.controllers.api.{}'.format(controller))

        super().register(*args, **kwargs)

api = API('api', __name__, url_prefix='/api')
