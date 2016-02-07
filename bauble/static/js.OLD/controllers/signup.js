'use strict';

angular.module('bauble-app')
    .controller('SignupCtrl', ['$scope', '$location', 'User',
        function ($scope, $location, User) {
            $scope.message = null;
            $scope.working = false;

            $scope.save = function() {
                $scope.working = true;
                console.log('$scope.user: ', $scope.user);
                $scope.user.username = $scope.user.email;
                console.log('$scope.user: ', $scope.user);
                User.signup($scope.user)
                    .success(function(data, status, headers, config) {
                        console.log('data: ', data);
                        User.local(data);
                        $location.path("/");
                    })
                    .error(function(data, status, headers, config) {
                        console.log('status: ', status);
                        switch (status) {
                        case 409:
                            $scope.message = "An account with this email already exists.";
                            break;
                        default:
                            $scope.message = "Error";
                        }
                    })
                    .finally(function() {
                        $scope.working = false;
                    });
            };
        }]);
