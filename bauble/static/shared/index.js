import AlertService from './alertService'
import DeleteModalFactory from './deleteModalFactory'
import overlayFactory from './overlayFactory'
import ResourceFactory from './resourceFactory'
import UserService from './userService'
import ViewMetaFactory from './viewMetaFactory'

export function init(app) {
    app.service('Alert', AlertService)
    app.factory('DeleteModal', DeleteModalFactory)
    app.factory('overlay', overlayFactory)
    app.factory('Resource', ResourceFactory)
    app.service('User', UserService)
    app.factory('ViewMeta', ViewMetaFactory)
}
