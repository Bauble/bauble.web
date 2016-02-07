const acc_type_values ={
    'Plant': 'Plant',
    'Seed': 'Seed/Spore',
    'Vegetative': 'Vegetative Part',
    'Tissue': 'Tissue Culture',
    'Other': 'Other',
    None: ''
};


export default function PlantEditCtrl ($scope, $location, $stateParams, $window,
                                       Alert, Accession, Plant, Location, overlay) {
    $scope.model = {
        accession: null,
        location: null,
    };

    $scope.plant = {
        accession_id: $location.search().accession,
        location_id: $location.search().location
    };

    $scope.header = $stateParams.id ? '' : 'New Plant';

    // isNew is inherited from the NewCtrl if this is a /new editor
    $scope.notes = $scope.plant.notes || [];
    $scope.propagation = {};
    $scope.location = {};

    $scope.activeTab = "general";

    $scope.acc_type_values = acc_type_values;

    // make sure we have the details
    if($stateParams.id) {
        overlay('loading...');
        Plant.get($stateParams.id, {embed: ['notes', 'accession', 'location']})
            .success(function(data, status, headers, config) {
                $scope.plant = data;
                $scope.header = $scope.plant.str;
                $scope.notes = $scope.plant.notes || [];
                $scope.model.location = data.location;
                $scope.model.accession = data.location;
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = 'Could not get plant details.';
                Alert.onErrorResponse(data, defaultMessage);
            })
            .finally(function() {
                overlay.clear();
            });
    } else {
        var loadingAccessions = false;
        var loadingLocation = false;
        if($scope.plant.accession_id) {
            loadingAccessions = true;
            Accession.get($scope.plant.accession_id, {embed: ["taxon"]})
                .success(function(data, status, headers, config) {
                    $scope.model.accession = data;
                })
                .error(function(data, status, headers, config) {
                    var defaultMessage = 'Could not get the accession details.';
                    Alert.onErrorResponse(data, defaultMessage);
                })
                .finally(function() {
                    loadingAccessions = false;
                    if(!loadingAccessions && !loadingLocation) {
                        overlay.clear();
                    }
                });
        }
        if($scope.plant.location_id) {
            loadingLocation = true;
            Location.get($scope.plant.accession_id)
                .success(function(data, status, headers, config) {
                    $scope.model.location = data;
                })
                .error(function(data, status, headers, config) {
                    var defaultMessage = 'Could not get the location details.';
                    Alert.onErrorResponse(data, defaultMessage);
                })
                .finally(function() {
                    loadingLocation = false;
                    if(!loadingAccessions && !loadingLocation) {
                        overlay.clear();
                    }
                });
        }
    }


    // get accessions for typeahead completions
    $scope.getAccessions = function($viewValue){
        return Accession.list({filter: {code: $viewValue + '%'}})
            .then(function(result) {
                return result.data;
            });
    };

    // get accessions for location
    $scope.getLocations = function($viewValue){
        return Location.list({filter: {code: $viewValue + '%'}})
            .then(function(result) {
                return result.data;
            });
    };

    $scope.alerts = [];
    $scope.closeAlert = function(index) {
        $scope.alerts.splice(index, 1);
    };

    $scope.cancel = function() {
        $window.history.back()
    };

    // called when the save button is clicked on the editor
    $scope.save = function() {
        //$scope.plant.notes = $scope.notes;
        $scope.plant.accession_id = $scope.model.accession.id;
        $scope.plant.location_id = $scope.model.location.id;
        Plant.save($scope.plant)
            .success(function(data, status, headers, config) {
                $window.history.back()
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = 'Could not save the plant.';
                Alert.onErrorResponse(data, defaultMessage);
            });

    };
}
