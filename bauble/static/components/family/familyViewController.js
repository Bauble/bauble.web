import _ from 'lodash'

export default function FamilyViewController ($scope, $stateParams, $state, $location,
                                              Alert, Family, DeleteModal) {

    $scope.family = null;
    $scope.counts = null;

    $scope.$watch('selected', function(selected) {
        $scope.family = $scope.selected;

        Family.get($scope.family, {'embed': ['synonyms']})
            .success(function(data, status, headers, config) {
                $scope.family = data;
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = 'Could not get family details';
                Alert.onErrorResponse(data, defaultMessage);
            });

        Family.count($scope.family, ['/genera', '/genera/taxa', '/genera/taxa/accessions',
                                     '/genera/taxa/accessions/plants'])
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
        DeleteModal(Family, $scope.family)
            .then(function(promise){
                Alert.add($scope.family.str + ' removed.');
            })
            .catch(function(result){
                if(result === 'cancel') {
                    return;
                }
                var defaultMessage = 'Could not get delete family.';
                Alert.onErrorResponse(result.data, defaultMessage);
            });
    };
}
