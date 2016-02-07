export default function LocationEditCtrl ($scope, $window, $stateParams, Plant, Location,
                                          Alert, overlay) {
    // isNew is inherited from the NewCtrl if this is a /new editor
    $scope.locaton = {};

    // make sure we have the details
    if($stateParams.id) {
        overlay('loading...');
        Location.get($stateParams.id)
            .success(function(data, status, headers, config) {
                $scope.location = data;
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = 'Could not get location details.';
                Alert.onErrorResponse(data, defaultMessage);
            })
            .finally(function() {
                overlay.clear();
            });
    }

    $scope.activeTab = "general";

    $scope.cancel = function() {
        $window.history.back();
    };

    $scope.alerts = [];
    $scope.closeAlert = function(index) {
        $scope.alerts.splice(index, 1);
    };

    // called when the save button is clicked on the editor
    $scope.save = function() {
        // TODO: we need a way to determine if this is a save on a new or existing
        // object an whether we whould be calling save or edit
        Location.save($scope.location)
            .success(function(data, status, headers, config) {
                $window.history.back();
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = 'Could not save the location.';
                Alert.onErrorResponse(data, defaultMessage);
            });
    };
}
