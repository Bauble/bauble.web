import TaxonViewFactory from './taxonViewFactory'

export function init(app) {
    app.factory('TaxonView', TaxonViewFactory)
}
