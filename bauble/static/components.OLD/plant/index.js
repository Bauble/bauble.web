import PlantEditController from './plantEditController'
import PlantFactory from './plantFactory'
import PlantViewFactory from './plantViewFactory'
import PlantViewController from './plantViewController'

export function init(app) {
    app.factory('PlantView', PlantViewFactory)
    app.factory('Plant', PlantFactory)
    app.controller('PlantViewController', PlantViewController)
    app.controller('PlantEditController', PlantEditController)
}
