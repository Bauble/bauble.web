'use strict';

angular.module('BaubleApp')
    .service('User', ['$http', 'apiRoot', function ($http, apiRoot) {

        var resourceUrl = [apiRoot, 'user'].join('/');

        function AuthorizedUser(user) {

            var _user = {
                getAuthHeader: function() {
                    return {'Authorization': 'Basic ' +
                            btoa(this.email + ':' + this.access_token)};
                },


                save: function(data) {
                    return $http({
                        url: [resourceUrl, data.id].join('/'),
                        method: 'PATCH',
                        data: data,
                        headers: user.getAuthHeader()
                    });
                }
            };

            return _.extend(user, _user);
        }


        return {

            extend: function(user) {
                return new AuthorizedUser(user);
            },

            login: function(email, password) {
                return $http({
                    url: [apiRoot, 'login'].join('/'),
                    method: 'GET',
                    headers: {'Authorization': 'Basic ' + btoa(email + ':' + password)}
                });
            },

            signup: function(user) {
                return $http({
                    url: resourceUrl,
                    method: 'POST',
                    data: user,
                    //headers: {'Authorization': 'Basic ' + btoa(email + ':' + password)}
                });
            },

            // setPassword = function(resource, password) {
            //     var config = {
            //         url: this.get_url_from_resource(resource) + "/password",
            //         headers: angular.extend(globals.getAuthHeader(), {
            //             'Content-Type': 'application/json'
            //         }),
            //         method: 'POST',
            //         data: { password: password }
            //     };
            //     return $http(config);
            // };

            local: function(user) {
                var key = 'user';

                if(user === null) {
                    // deleter
                    localStorage.removeItem(key);
                } else {
                    if(user) {
                        // setter
                        localStorage.setItem(key, JSON.stringify(user));
                    } else {
                        // getter
                        var data = localStorage.getItem(key);
                        return data === null ? data : this.extend(JSON.parse(data));
                    }
                }
            },

            forgotPassword: function(email) {
                return $http({
                    url: [apiRoot, 'forgot-password'].join('/'),
                    method: 'POST',
                    params: {
                        email: email
                    }
                });
            },

            resetPassword: function(email, token, password) {
                return $http({
                    url: [apiRoot, 'reset-password'].join('/'),
                    method: 'POST',
                    data: {
                        email: email,
                        token: token,
                        password: password
                    }
                });
            }
        };
    }]);
