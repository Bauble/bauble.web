export default function TaxonView () {
    return {
        editor: "/static/components/taxon/edit.html",
        view: "/static/components/taxon/view.html",

        buttons: [
            { name: "Edit", event: "taxon-edit" },
            { name: "Add Accession", event: "taxon-addaccession" },
            { name: "Delete", event: "taxon-delete" }
        ]
    };
}
