'use strict';

angular.module('bauble-app')
  .controller('ResetPasswordCtrl', ['$scope', '$location', '$stateParams', 'User',
    function ($scope, $location, $stateParams, User) {

        $scope.token = $stateParams.token;
        $scope.email = $location.search().email;

        // TODO: we need a progress spinner here

        $scope.submit = function(email, token, password) {
            User.resetPassword(email, token, password)
                .success(function(data, status, headers, config) {
                    // login
                    console.log('data: ', data);
                    User.local(data);
                    $location.path("/");
                })
                .error(function(data, status, headers, config) {
                    $scope.message = "Could not reset password";
                });
        };
    }]);
