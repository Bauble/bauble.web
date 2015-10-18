'use strict';

angular.module('BaubleApp')
    .factory('Search', function ($http, apiRoot, User) {

        return {
            query: function(q) {
                var user = User.local();
                var config = {
                    url: apiRoot + "/search",
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
