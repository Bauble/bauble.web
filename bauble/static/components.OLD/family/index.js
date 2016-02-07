import FamilyEditController from './familyEditController'
import FamilyFactory from './familyFactory'
import FamilyViewFactory from './familyViewFactory'
import FamilyViewController from './familyViewController'

export function init(app) {
    app.factory('FamilyView', FamilyViewFactory)
    app.factory('Family', FamilyFactory)
    app.controller('FamilyEditController', FamilyEditController)
    app.controller('FamilyViewController', FamilyViewController)
}
