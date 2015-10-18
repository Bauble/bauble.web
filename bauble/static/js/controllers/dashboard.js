'use strict';

angular.module('BaubleApp')
  .controller('DashboardCtrl', ['$scope', '$location',
    function ($scope, $location) {
        $scope.search = function(value){
            $location.path('/search').search('q', value);
        };
    }]);
