export default function FamilyFactory (Resource, $http) {
    var resource = Resource('/api/family', 'family');

    resource.getSynonym = function(family, synonym){
        return $http({
            url: [resource.resourceUrl, family.id || family, 'synonyms', synonym.id||synonym].join('/'),
            method: 'GET',
            headers: this._getAuthHeader()
        });
    };

    resource.listSynonyms = function(family){
        return $http({
            url: [resource.resourceUrl, family.id || family, 'synonyms'].join('/'),
            method: 'GET',
            headers: this._getAuthHeader()
        });
    };

    resource.addSynonym = function(family, synonym){
        return $http({
            url: [resource.resourceUrl, family.id || family, 'synonyms'].join('/'),
            method: 'POST',
            data: synonym,
            headers: this._getAuthHeader()
        });
    };

    resource.removeSynonym = function(family, synonym){
        return $http({
            url: [resource.resourceUrl, family.id || family, 'synonyms',
                  synonym.id || synonym].join('/'),
            method: 'DELETE',
            headers: this._getAuthHeader()
        });
    };
    return resource;
}
