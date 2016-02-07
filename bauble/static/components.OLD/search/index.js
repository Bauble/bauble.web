import SearchFactory from './searchFactory'
import SearchCtrl from './searchController'

export function init(app) {
    app.factory('Search', SearchFactory)
    app.controller('SearchCtrl', SearchCtrl)
}
