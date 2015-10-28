import _ from 'lodash'

export default function GenusFactory (Resource, $http) {
    var resource =  Resource('/api/genus', 'genus');

    resource.getSynonym = function(genus, synonym){
        return $http({
            url: [resource.resourceUrl, genus.id || genus, 'synonyms', synonym.id||synonym].join('/'),
            method: 'GET',
            headers: this._getAuthHeader()
        });
    };

    resource.listSynonyms = function(genus){
        return $http({
            url: [resource.resourceUrl, genus.id || genus, 'synonyms'].join('/'),
            method: 'GET',
            headers: this._getAuthHeader()
        });
    };

    resource.addSynonym = function(genus, synonym){
        return $http({
            url: [resource.resourceUrl, genus.id || genus, 'synonyms'].join('/'),
            method: 'POST',
            data: synonym,
            headers: this._getAuthHeader()
        });
    };

    resource.removeSynonym = function(genus, synonym){
        return $http({
            url: [resource.resourceUrl, genus.id || genus, 'synonyms',
                  synonym.id || synonym].join('/'),
            method: 'DELETE',
            headers: this._getAuthHeader()
        });
    };

    return resource;
}
