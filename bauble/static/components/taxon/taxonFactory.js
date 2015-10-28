import _ from 'lodash'

export default function TaxonFactory (Resource, $http) {
    var resource =  Resource('/api/taxon');

    resource.getSynonym = function(taxon, synonym){
        return $http({
            url: [resource.resourceUrl, taxon.id || taxon, 'synonyms', synonym.id||synonym].join('/'),
            method: 'GET',
            headers: this._getAuthHeader()
        });
    };

    resource.listSynonyms = function(taxon){
        return $http({
            url: [resource.resourceUrl, taxon.id || taxon, 'synonyms'].join('/'),
            method: 'GET',
            headers: this._getAuthHeader()
        });
    };

    resource.addSynonym = function(taxon, synonym){
        return $http({
            url: [resource.resourceUrl, taxon.id || taxon, 'synonyms'].join('/'),
            method: 'POST',
            data: synonym,
            headers: this._getAuthHeader()
        });
    };

    resource.removeSynonym = function(taxon, synonym){
        return $http({
            url: [resource.resourceUrl, taxon.id || taxon, 'synonyms',
                  synonym.id || synonym].join('/'),
            method: 'DELETE',
            headers: this._getAuthHeader()
        });
    };

    resource.listNames = function(taxon){
        return $http({
            url: [resource.resourceUrl, taxon.id || taxon, 'names'].join('/'),
            method: 'GET',
            headers: this._getAuthHeader()
        });
    };

    // save or update a vernacular name
    resource.saveName = function(taxon, name){
        var url = [resource.resourceUrl, taxon.id || taxon, 'names'].join('/');
        url += name.id ? ('/' + name.id) : '';
        return $http({
            url: url,
            method: name.id ? 'PATCH' : 'POST',
            data: name,
            headers: this._getAuthHeader()
        });
    };

    resource.removeName = function(taxon, name){
        return $http({
            url: [resource.resourceUrl, taxon.id || taxon, 'names',
                  name.id || name].join('/'),
            method: 'DELETE',
            headers: this._getAuthHeader()
        });
    };


    resource.listDistributions = function(taxon){
        return $http({
            url: [resource.resourceUrl, taxon.id || taxon, 'distributions'].join('/'),
            method: 'GET',
            headers: this._getAuthHeader()
        });
    };

    // save a new geography as a distribution
    resource.addDistribution = function(taxon, distribution){
        var url = [resource.resourceUrl, taxon.id || taxon, 'distributions'].join('/');
        return $http({
            url: url,
            method: 'POST',
            data: distribution,
            headers: this._getAuthHeader()
        });
    };

    resource.removeDistribution = function(taxon, distribution){
        return $http({
            url: [resource.resourceUrl, taxon.id || taxon, 'distributions',
                  distribution.id || distribution].join('/'),
            method: 'DELETE',
            headers: this._getAuthHeader()
        });
    };

    return resource;
}
