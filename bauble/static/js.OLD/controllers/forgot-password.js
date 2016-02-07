'use strict';

angular.module('bauble-app')
  .controller('ForgotPasswordCtrl', ['$scope', '$stateParams', 'User',
    function ($scope, $stateParams, User) {

        $scope.submit = function(email) {
            console.log('email: ', email);
            User.forgotPassword(email)
                .success(function(data, status, headers, config) {
                    $scope.success = true;
                })
                .error(function(data, status, headers, config) {
                    $scope.message = "Could not reset password";
                });
        };

    }]);
