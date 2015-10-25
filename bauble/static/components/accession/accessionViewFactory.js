export default function AccessionView () {
    return {
        editor: "/static/partials/accession-edit.html",
        view: "/static/partials/accession-view.html",

        buttons: [
            { name: "Edit", event: "accession-edit" },
            { name: "Add Plant", event: 'accession-addplant' }, // add plant to selected Accession,
            { name: "Delete",  event: 'accession-delete' } // delete the selected Accession
        ]
    };
}
