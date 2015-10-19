const app = angular.module('bauble-app')

app.controller('DashboardCtrl', function ($scope, $location) {
    $scope.search = function(value){
        $location.path('/search').search('q', value);
    };
});
