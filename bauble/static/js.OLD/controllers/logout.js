'use strict';

angular.module('bauble-app')
    .controller('LogoutCtrl', function ($scope, User) {
        User.local(null);
        $scope.$emit('logout');
    });
