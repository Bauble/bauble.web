import FamilyViewFactory from './familyViewFactory'
import FamilyEditController from './familyEditController'
import FamilyFactory from './familyFactory'

console.log('FamilyFactory: ', FamilyFactory);

export function init(app) {
    app.factory('FamilyView', FamilyViewFactory)
    app.factory('Family', FamilyFactory)
    app.controller('FamilyEditController', FamilyEditController)
}
