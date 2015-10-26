export default function FamilyViewFactory () {
    return {
        editor: "/static/components/family/family-edit.html",
        view: "/static/components/family/family-view.html",

        buttons: [
            { name: "Edit", event: "family-edit" },
            { name: "Add Genus", event: "family-addgenus" }, // add genus to selected Family,
            { name: "Delete", event: "family-delete"} // delete the selected Family
        ]
    };
}
