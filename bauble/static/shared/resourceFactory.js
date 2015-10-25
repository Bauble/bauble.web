export default function ResourceFactory ($http, User) {
    return function(resourceRoot, name) {
        var resourceUrl = resourceRoot;

        return {
            resourceUrl: resourceRoot,
            name: name,

            _getAuthHeader: function() {
                var user = User.local();
                return user ? user.getAuthHeader() : {};
            },

            /*
             * resource can be an ID, a ref or an object with a ref
             */
            get: function(resource, config) {
                var params = config ? _.pick(config, ['pick', 'embed']) : null;
                return $http({
                    url: [resourceUrl, resource.id || resource].join('/'),
                    method: 'GET',
                    headers: this._getAuthHeader(),
                    params: params
                });
            },

            list: function(config) {
                var params = config ? _.pick(config, ['embed']) : null;
                var url = resourceUrl;
                if(config && angular.isDefined(config.filter)) {
                    url += '?filter=' + encodeURIComponent(JSON.stringify(config.filter));
                }

                return $http({
                    url: url,
                    method: 'GET',
                    headers: this._getAuthHeader(),
                    params: params || null
                });
            },

            query: function(options) {
                options = angular.extend({
                    q: "",
                    relations: ""
                }, options);
                var config = {
                    url: resourceUrl,
                    method: 'GET',
                    params: {
                        q: options.q || "",
                        relations: options.relations || ""
                    },
                    headers: this._getAuthHeader()
                };
                return $http(config);
            },

            save: function (data) {
                // if the data has a ref then it already exists in the
                // database and should be updated instead of creating a new
                // one
                return $http({
                    url: data.id ? [resourceUrl, data.id].join('/') : resourceUrl,
                    method: data.id ? 'PATCH' : 'POST',
                    data: data,
                    headers: this._getAuthHeader()
                });
            },

            remove: function(resource) {
                var config = {
                    method: 'DELETE',
                    url: resourceUrl + '/' + (resource.id || resource),
                    headers: this._getAuthHeader()
                };
                return $http(config);
            },

            getSchema: function(scalars_only) {
                var config = {
                    method: 'GET',
                    url: resourceUrl + '/schema',
                    headers: this._getAuthHeader(),
                    params: scalars_only ?
                        { flags: 'scalars_only' } : undefined
                };
                return $http(config);
            },

            count: function(resource, relation) {
                return $http({
                    url: [resourceUrl, resource.id || resource, 'count'].join('/'),
                    method: 'GET',
                    headers: this._getAuthHeader(),
                    params: {
                        relation: relation
                    }
                });
                // var config = {
                //     method: 'GET',
                //     url: this.get_url_from_resource(resource) +
                //         relation + "/count",
                //     headers: globals.getAuthHeader()
                // };
                // return $http(config);
            }
        };
    };
}



// Genus service for CRUD genus types
// app.factory('Genus', function($resource, $http) {
//     var resource =  $resource('/genus');

//     resource.getSynonym = function(genus, synonym){
//         return $http({
//             url: [resource.resourceUrl, genus.id || genus, 'synonyms', synonym.id||synonym].join('/'),
//             method: 'GET',
//             headers: this._getAuthHeader()
//         });
//     };

//     resource.listSynonyms = function(genus){
//         return $http({
//             url: [resource.resourceUrl, genus.id || genus, 'synonyms'].join('/'),
//             method: 'GET',
//             headers: this._getAuthHeader()
//         });
//     };

//     resource.addSynonym = function(genus, synonym){
//         return $http({
//             url: [resource.resourceUrl, genus.id || genus, 'synonyms'].join('/'),
//             method: 'POST',
//             data: synonym,
//             headers: this._getAuthHeader()
//         });
//     };

//     resource.removeSynonym = function(genus, synonym){
//         return $http({
//             url: [resource.resourceUrl, genus.id || genus, 'synonyms',
//                   synonym.id || synonym].join('/'),
//             method: 'DELETE',
//             headers: this._getAuthHeader()
//         });
//     };

//     return resource;

// })

// // Taxon service for CRUD taxon types
// app.factory('Taxon', function($resource, $http) {
//     var resource =  $resource('/taxon');

//     resource.getSynonym = function(taxon, synonym){
//         return $http({
//             url: [resource.resourceUrl, taxon.id || taxon, 'synonyms', synonym.id||synonym].join('/'),
//             method: 'GET',
//             headers: this._getAuthHeader()
//         });
//     };

//     resource.listSynonyms = function(taxon){
//         return $http({
//             url: [resource.resourceUrl, taxon.id || taxon, 'synonyms'].join('/'),
//             method: 'GET',
//             headers: this._getAuthHeader()
//         });
//     };

//     resource.addSynonym = function(taxon, synonym){
//         return $http({
//             url: [resource.resourceUrl, taxon.id || taxon, 'synonyms'].join('/'),
//             method: 'POST',
//             data: synonym,
//             headers: this._getAuthHeader()
//         });
//     };

//     resource.removeSynonym = function(taxon, synonym){
//         return $http({
//             url: [resource.resourceUrl, taxon.id || taxon, 'synonyms',
//                   synonym.id || synonym].join('/'),
//             method: 'DELETE',
//             headers: this._getAuthHeader()
//         });
//     };

//     resource.listNames = function(taxon){
//         return $http({
//             url: [resource.resourceUrl, taxon.id || taxon, 'names'].join('/'),
//             method: 'GET',
//             headers: this._getAuthHeader()
//         });
//     };

//     // save or update a vernacular name
//     resource.saveName = function(taxon, name){
//         var url = [resource.resourceUrl, taxon.id || taxon, 'names'].join('/');
//         url += name.id ? ('/' + name.id) : '';
//         return $http({
//             url: url,
//             method: name.id ? 'PATCH' : 'POST',
//             data: name,
//             headers: this._getAuthHeader()
//         });
//     };

//     resource.removeName = function(taxon, name){
//         return $http({
//             url: [resource.resourceUrl, taxon.id || taxon, 'names',
//                   name.id || name].join('/'),
//             method: 'DELETE',
//             headers: this._getAuthHeader()
//         });
//     };


//     resource.listDistributions = function(taxon){
//         return $http({
//             url: [resource.resourceUrl, taxon.id || taxon, 'distributions'].join('/'),
//             method: 'GET',
//             headers: this._getAuthHeader()
//         });
//     };

//     // save a new geography as a distribution
//     resource.addDistribution = function(taxon, distribution){
//         var url = [resource.resourceUrl, taxon.id || taxon, 'distributions'].join('/');
//         return $http({
//             url: url,
//             method: 'POST',
//             data: distribution,
//             headers: this._getAuthHeader()
//         });
//     };

//     resource.removeDistribution = function(taxon, distribution){
//         return $http({
//             url: [resource.resourceUrl, taxon.id || taxon, 'distributions',
//                   distribution.id || distribution].join('/'),
//             method: 'DELETE',
//             headers: this._getAuthHeader()
//         });
//     };

//     return resource;
// })

// // Accession service for CRUD accession types
// app.factory('Accession', function($resource) {
//     return $resource('/accession');
// })

// // Source service for CRUD source types
// app.factory('Source', function($resource) {
//     return $resource('/source');
// })

// // Plant service for CRUD plant types
// app.factory('Plant', function($resource) {
//     return $resource('/plant');
// })

// // Location service for CRUD location types
// app.factory('Location', function($resource) {
//     return $resource('/location');
// })

// // Organization service for CRUD location types
// app.factory('Organization', function($http, $resource) {
//     var resource =  $resource('/organization');

//     resource.invite = function(organization, email, message) {
//         return $http({
//             url: [this.resourceUrl, organization.id || organization, 'invite'].join('/'),
//             method: 'POST',
//             headers: this._getAuthHeader(),
//             data: {
//                 email: email,
//                 message: message
//             }
//         });
//     };

//     return resource;
// })


// // Report service.
// app.factory('Report', function($http, $resource) {
//     var resource = $resource('/report');

//     resource.csv = function(report) {
//         return $http({
//             url: [this.resourceUrl, report.id || report, 'csv'].join('/'),
//             method: 'GET',
//             headers: this._getAuthHeader()
//         });
//     };

//     return resource;
// });
