export default function ViewMetaFactory (FamilyView, GenusView, TaxonView, AccessionView,
                                         PlantView, LocationView) {
    console.log('FamilyView: ', FamilyView);
    return {
        getView: function(resource)  {
            // allow get the view based on the ref
            switch(true) {
            case /families/.test(resource):
                return FamilyView;
            case /genera/.test(resource):
                return GenusView;
            case /taxa/.test(resource):
                return TaxonView;
            case /accessions/.test(resource):
                return AccessionView;
            case /plants/.test(resource):
                console.log(resource);
                return PlantView;
            case /locations/.test(resource):
                return LocationView;

                // case /\/family/.test(ref):
                //     return FamilyView;
                // case /\/genus/.test(ref):
                //     return GenusView;
                // case /\/taxon/.test(ref):
                //     return TaxonView;
                // case /\/accession/.test(ref):
                //     return AccessionView;
                // case /\/plant/.test(ref):
                //     return PlantView;
                // case /\/location/.test(ref):
                //     return LocationView;
            default:
                return null;
            }
        },

        families: FamilyView,
        genera: GenusView,
        taxa: TaxonView,
        accessions: AccessionView,
        plants: PlantView,
        locations: LocationView,
        'family': FamilyView,
        'genus': GenusView,
        'taxon': TaxonView,
        'accession': AccessionView,
        'plant': PlantView,
        'location': LocationView
    };
}

    // .factory('FamilyView', [function() {
    //     return {
    //         editor: "/static/partials/family-edit.html",
    //         view: "/static/partials/family-view.html",

    //         buttons: [
    //             { name: "Edit", event: "family-edit" },
    //             { name: "Add Genus", event: "family-addgenus" }, // add genus to selected Family,
    //             { name: "Delete", event: "family-delete"} // delete the selected Family
    //         ]
    //     };
    // }])

    // .factory('GenusView', [function() {
    //     return {
    //         editor: "/static/partials/genus-edit.html",
    //         view: "/static/partials/genus-view.html",

    //         buttons: [
    //             { name: "Edit", event: "genus-edit" },
    //             { name: "Add Taxon", event: "genus-addtaxon" }, // add Taxon to selected Genus
    //             { name: "Delete", event: "genus-delete" }  // delete the selected Genus
    //         ]
    //     };
    // }])

    // .factory('TaxonView', [function() {
    //     return {
    //         editor: "/static/partials/taxon-edit.html",
    //         view: "/static/partials/taxon-view.html",

    //         buttons: [
    //             { name: "Edit", event: "taxon-edit" },
    //             { name: "Add Accession", event: "taxon-addaccession" }, // add accession to selected Taxon
    //             { name: "Delete", event: "taxon-delete" } // delete the selected Taxon
    //         ]
    //     };
    // }])

    // .factory('AccessionView', [function() {
    //     return {
    //         editor: "/static/partials/accession-edit.html",
    //         view: "/static/partials/accession-view.html",

    //         buttons: [
    //             { name: "Edit", event: "accession-edit" },
    //             { name: "Add Plant", event: 'accession-addplant' }, // add plant to selected Accession,
    //             { name: "Delete",  event: 'accession-delete' } // delete the selected Accession
    //         ]
    //     };
    // }])

    // .factory('PlantView', [function() {
    //     return {
    //         editor: "/static/partials/plant-edit.html",
    //         view: "/static/partials/plant-view.html",
    //         buttons: [
    //             { name: "Edit", event: 'plant-edit' },
    //             { name: "Delete", event: 'plant-delete' } // delete the selected Plant
    //         ]
    //     };
    // }])

    // .factory('LocationView', [function() {
    //     return {
    //         editor: "/static/partials/location-edit.html",
    //         view: "/static/partials/location-view.html",
    //         buttons: [
    //             { name: "Edit", event: 'location-edit' },
    //             { name: "Delete", event: 'location-delete' } // delete the selected Location
    //         ]
    //     };
    // }]);
