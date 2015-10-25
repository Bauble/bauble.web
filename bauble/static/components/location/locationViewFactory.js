export default function LocationView () {
    return {
        editor: "/static/partials/location-edit.html",
        view: "/static/partials/location-view.html",
        buttons: [
            { name: "Edit", event: 'location-edit' },
            { name: "Delete", event: 'location-delete' } // delete the selected Location
        ]
    };
}
