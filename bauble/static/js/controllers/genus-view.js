'use strict';

angular.module('BaubleApp')
  .controller('GenusViewCtrl', ['$scope', '$location', 'Alert', 'Genus', 'DeleteModal',
    function ($scope, $location, Alert, Genus, DeleteModal) {

        $scope.genus = null;
        $scope.counts = null;

        $scope.$watch('selected', function(selected) {
            $scope.genus = $scope.selected;

            Genus.get($scope.genus, {embed: ['synonyms', 'family']})
                .success(function(data, status, headers, config) {
                    $scope.genus = data;
                })
                .error(function(data, status, headers, config) {
                    var defaultMessage = 'Could not get genus details';
                    Alert.onErrorResponse(data, defaultMessage);
                });


            Genus.count($scope.genus, ['/taxa', '/taxa/accessions', '/taxa/accessions/plants'])
                .success(function(data, status, headers, config) {
                    $scope.counts = data;
                    _.each(data, function(value, key) {
                        // keys are in '/' notation
                        key = _.last(key.split('/'));
                        $scope.counts[key] = value;
                    });
                })
                .error(function(data, status, headers, config) {
                    var defaultMessage = "Could not count the relations";
                    Alert.onErrorResponse(data, defaultMessage);
                });
        });

        $scope.delete = function() {
            DeleteModal(Genus, $scope.genus)
                .then(function(promise){
                    Alert.add($scope.genus.str + ' removed.');
                })
                .catch(function(result){
                    if(result === 'cancel') {
                        return;
                    }
                    var defaultMessage = 'Could not get delete genus.';
                    Alert.onErrorResponse(result.data, defaultMessage);
                });
        };
    }]);
