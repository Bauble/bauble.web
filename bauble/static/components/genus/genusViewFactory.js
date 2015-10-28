export default function GenusViewFactory () {
    return {
        editor: "/static/components/genus/edit.html",
        view: "/static/components/genus/view.html",

        buttons: [
            { name: "Edit", event: "genus-edit" },
            { name: "Add Taxon", event: "genus-addtaxon" }, // add Taxon to selected Genus
            { name: "Delete", event: "genus-delete" }  // delete the selected Genus
        ]
    }
}
