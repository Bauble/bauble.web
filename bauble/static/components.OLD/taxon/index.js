import TaxonEditController from './taxonEditController'
import TaxonFactory from './taxonFactory'
import TaxonViewFactory from './taxonViewFactory'
import TaxonViewController from './taxonViewController'

export function init(app) {
    app.factory('TaxonView', TaxonViewFactory)
    app.factory('Taxon', TaxonFactory)
    app.controller('TaxonViewController', TaxonViewController)
    app.controller('TaxonEditController', TaxonEditController)
}
