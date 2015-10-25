import GenusEditController from './genusEditController'
import GenusFactory from './genusFactory'
import GenusViewFactory from './genusViewFactory'
import GenusViewController from './genusViewController'

export function init(app) {
    app.factory('GenusView', GenusViewFactory)
    app.factory('Genus', GenusFactory)
    app.controller('GenusViewController', GenusViewController)
    app.controller('GenusEditController', GenusEditController)
}
