export default function PlantView () {
    return {
        editor: "/static/partials/plant-edit.html",
        view: "/static/partials/plant-view.html",
        buttons: [
            { name: "Edit", event: 'plant-edit' },
            { name: "Delete", event: 'plant-delete' } // delete the selected Plant
        ]
    };
}
