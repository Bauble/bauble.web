import AccessionEditController from './accessionEditController'
import AccessionFactory from './accessionFactory'
import AccessionViewFactory from './accessionViewFactory'
import AccessionViewController from './accessionViewController'
import SourceFactory from './sourceFactory'
import SourceDetailEditCtrl from './sourceEditController'

export function init(app) {
    app.factory('AccessionView', AccessionViewFactory)
    app.factory('Accession', AccessionFactory)
    app.controller('AccessionViewController', AccessionViewController)
    app.controller('AccessionEditController', AccessionEditController)
    app.factory('Source', SourceFactory)
    app.controller('SourceDetailEditCtrl', SourceDetailEditCtrl)
}
