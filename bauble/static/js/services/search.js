const app = angular.module('bauble-app')

app.factory('Search', function ($http, User) {
    return {
        query: function(q) {
            var user = User.local();
            var config = {
                url: "/search",
                method: 'GET',
                params: {
                    q: q
                },
                headers: user ? user.getAuthHeader() : null
                // headers: angular.extend(globals.getAuthHeader(), {
                //     'Accept': 'application/json;depth=1'
                // })
            };
            return $http(config);
        }
    };
});
