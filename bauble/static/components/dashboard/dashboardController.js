export default function DashboardCtrl ($scope, $location) {
    $scope.search = function(value){
        $location.path('/search').search('q', value);
    };
}
