'use strict';

angular.module('bauble-app')
    .controller('PlantViewCtrl', function ($scope, $location, Alert, Plant, DeleteModal) {

        $scope.plant = null;

        $scope.$watch('selected', function(selected) {
            $scope.plant = $scope.selected;

            Plant.get($scope.plant, {embed: ['location', 'accession']})
                .success(function(data, status, headers, config) {
                    $scope.plant = data;
                    var accLength = data.accession.code.length;
                    $scope.accCode = data.str.substring(0, accLength);
                    $scope.plantCode = data.str.substring(accLength, data.str.length);
                })
                .error(function(data, status, headers, config) {
                    var defaultMessage = "Could not get plant details.";
                    Alert.onErrorResponse(data, defaultMessage);
                });
        });


        $scope.delete = function() {
            DeleteModal(Plant, $scope.plant)
                .then(function(promise){
                    Alert.add($scope.plant.str + ' removed.');
                })
                .catch(function(result){
                    if(result === 'cancel') {
                        return;
                    }
                    var defaultMessage = 'Could not get delete plant.';
                    Alert.onErrorResponse(result.data, defaultMessage);
                });
        };
    });
