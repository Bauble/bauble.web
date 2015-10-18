'use strict';

angular.module('BaubleApp')
    .controller('LogoutCtrl', function ($scope, User) {
        User.local(null);
        $scope.$emit('logout');
    });
