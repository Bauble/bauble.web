const app = angular.module('bauble-app')

app.controller('AccessionViewCtrl', function ($scope, $location, $state, Alert, Accession,
                                              DeleteModal) {

    $scope.accession = null;
    $scope.counts = null;

    $scope.$watch('selected', function(selected) {
        $scope.accession = $scope.selected;

        Accession.get($scope.accession)
            .success(function(data, status, headers, config) {
                $scope.accession = data;
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = 'Could not get accession details';
                Alert.onErrorResponse(data, defaultMessage);
            });

        Accession.count($scope.accession, ['/plants'])
            .success(function(data, status, headers, config) {
                $scope.counts = data;
                _.each(data, function(value, key) {
                    // keys are in '/' notation
                    key = _.last(key.split('/'));
                    $scope.counts[key] = value;
                });
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = "Count not count the relations";
                Alert.onErrorResponse(data, defaultMessage);
            });
    });


    $scope.delete = function() {
        DeleteModal(Accession, $scope.accession)
            .then(function(promise){
                Alert.add($scope.accession.str + ' removed.');
            })
            .catch(function(result){
                if(result === 'cancel') {
                    return;
                }
                var defaultMessage = 'Could not get delete accession.';
                Alert.onErrorResponse(result.data, defaultMessage);
            });
    };
});
