export default function GenusViewFactory () {
    return {
        editor: "/static/partials/genus-edit.html",
        view: "/static/partials/genus-view.html",

        buttons: [
            { name: "Edit", event: "genus-edit" },
            { name: "Add Taxon", event: "genus-addtaxon" }, // add Taxon to selected Genus
            { name: "Delete", event: "genus-delete" }  // delete the selected Genus
        ]
    };
}
