export default function AccessionViewFactory () {
    return {
        editor: "/static/components/accession/edit.html",
        view: "/static/components/accession/view.html",

        buttons: [
            { name: "Edit", event: "accession-edit" },
            { name: "Add Plant", event: 'accession-addplant' }, // add plant to selected Accession,
            { name: "Delete",  event: 'accession-delete' } // delete the selected Accession
        ]
    }
}
