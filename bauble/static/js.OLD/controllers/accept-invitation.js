const app = angular.module('bauble-app')

app.controller('AcceptInvitationCtrl', function($scope, $http, $location, $stateParams,
                                                 User, Alert, Invitation) {
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

});
