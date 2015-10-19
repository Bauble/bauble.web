const app = angular.module('bauble-app')

app.factory('Invitation', function ($http) {

    return {
        get: function(token) {
            return $http({
                url: ['/invitations', token].join('/'),
                method: 'GET'
            });
        },

        accept: function(token, password) {
            return $http({
                url: ['/invitations', token].join('/'),
                method: 'POST',
                data: {
                    password: password
                }
            });
        }
    };

});
