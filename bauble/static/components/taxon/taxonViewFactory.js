export default function TaxonView () {
    return {
        editor: "/static/components/taxon/edit.html",
        view: "/static/components/taxon/view.html",

        buttons: [
            { name: "Edit", event: "taxon-edit" },
            { name: "Add Accession", event: "taxon-addaccession" }, // add accession to selected Taxon
            { name: "Delete", event: "taxon-delete" } // delete the selected Taxon
        ]
    };
}
