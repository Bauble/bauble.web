'use strict';

angular.module('bauble-app')
    .controller('LoginCtrl',
        function ($scope, $location, User) {

            $scope.message = null;
            $scope.working = false;

            $scope.login = function() {
                $scope.working = true;
                User.login($scope.email, $scope.password)
                    .success(function(data, status, headers, config) {
                        User.local(data);
                        $scope.$emit('login');
                        $location.url('/');
                    })
                    .error(function(data, status, headers, config) {
                        switch(status) {
                        case 500:
                            $scope.message = 'Server Error.';
                            break;
                        case 401:
                            $scope.message = 'Invalid username or password';
                            break;
                        default:
                            $scope.message = 'Unknown Error.';
                        }
                    })
                    .finally(function() {
                        $scope.working = false;
                    });
            };
        });
