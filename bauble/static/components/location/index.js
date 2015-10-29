import LocationEditController from './locationEditController'
import LocationFactory from './locationFactory'
import LocationViewFactory from './locationViewFactory'
import LocationViewController from './locationViewController'

export function init(app) {
    app.factory('LocationView', LocationViewFactory)
    app.factory('Location', LocationFactory)
    app.controller('LocationViewController', LocationViewController)
    app.controller('LocationEditController', LocationEditController)
}
