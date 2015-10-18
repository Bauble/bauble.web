'use strict';

angular.module('BaubleApp')
  .factory('Invitation', ['$http', 'apiRoot',
    function ($http, apiRoot) {

        return {
            get: function(token) {
                return $http({
                    url: [apiRoot, 'invitations', token].join('/'),
                    method: 'GET'
                });
            },

            accept: function(token, password) {
                return $http({
                    url: [apiRoot, 'invitations', token].join('/'),
                    method: 'POST',
                    data: {
                        password: password
                    }
                });
            }
        };

    }]);
