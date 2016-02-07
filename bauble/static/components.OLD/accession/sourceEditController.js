const source_type_values = {
    'Expedition': 'Expedition',
    'GeneBank': 'Gene Bank',
    'BG': 'Botanic Garden or Arboretum',
    'Research/FieldStation': 'Research/Field Station',
    'Staff': 'Staff member',
    'UniversityDepartment': 'University Department',
    'Club': 'Horticultural Association/Garden Club',
    'MunicipalDepartment': 'Municipal department',
    'Commercial': 'Nursery/Commercial',
    'Individual': 'Individual',
    'Other': 'Other',
    'Unknown': 'Unknown',
    null: ''
};

export default function SourceDetailEditCtrl ($scope, $uibModalInstance, Alert, Source,
                                              sourceDetail) {

    $scope.sourceDetail = sourceDetail;

    $scope.source_type_values = source_type_values;

    $scope.save = function() {
        Source.save($scope.sourceDetail)
            .success(function(data, status, headers, config) {
                $uibModalInstance.close(data);
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = "Could not save source detail";
                Alert.onErrorResponse(data, defaultMessage);
            });
    };

    $scope.cancel = function() {
        $uibModalInstance.dismiss('cancel');
    };
}
