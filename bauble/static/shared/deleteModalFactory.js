export default function DeleteModalFactory ($uibModal) {

    return function(resource, resourceData, str) {

        str = str || resourceData.str;

        var modalInstance = $uibModal.open({
            templateUrl: '/static/partials/delete-modal.html',
            controller: function($scope, $modalInstance) {

                $scope.str = str;
                //$scope.resourceName = resource.name;

                $scope.delete = function() {
                    // return the $httpPromise
                    $modalInstance.close(resource.remove(resourceData));
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };

            }
        });

        return modalInstance.result;
    };
}
