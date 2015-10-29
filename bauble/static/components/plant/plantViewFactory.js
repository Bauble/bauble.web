export default function PlantView () {
    return {
        editor: "/static/components/edit.html",
        view: "/static/components/view.html",
        buttons: [
            { name: "Edit", event: 'plant-edit' },
            { name: "Delete", event: 'plant-delete' } // delete the selected Plant
        ]
    };
}
