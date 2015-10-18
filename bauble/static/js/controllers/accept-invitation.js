'use strict';

angular.module('BaubleApp')
  .controller('AcceptInvitationCtrl',
   ['$scope', '$http', '$location', '$stateParams', 'apiRoot', 'User', 'Alert', 'Invitation',
    function($scope, $http, $location, $stateParams, apiRoot, User, Alert, Invitation) {

        $scope.loading = true;
        $scope.token = $stateParams.token;

        Invitation.get($scope.token)
            .success(function(data, status, headers, config) {
                $scope.invitation = data;
                $scope.tokenFound = true;
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = 'Could not get the invitation.';
                Alert.onErrorResponse(data, defaultMessage);
            })
            .finally(function() {
                $scope.loading = false;
                console.log('$scope.loading: ', $scope.loading);
            });

        $scope.save = function(token, password) {
            Invitation.accept(token, password)
                .success(function(data, status, headers, config) {
                    User.local(data);
                    $location.path("/");
                })
                .error(function(data, status, headers, config) {
                    var defaultMessage = 'Could not accept the invitation.';
                    Alert.onErrorResponse(data, defaultMessage);
                });
        };

    }]);
