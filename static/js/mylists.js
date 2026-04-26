// new list button
const new_list_button = document.getElementById("new-list-button");
new_list_button.addEventListener("click", function() {
    // show popup
    document.getElementById("new-list-overlay").style.display = "flex";
    document.getElementById("backdrop-first").style.display = "block";
})

// cancel button
const cancel_button = document.getElementById("cancel-button");
cancel_button.addEventListener("click", function() {
    // get rid of popup and do nothing
    document.getElementById("new-list-overlay").style.display = "none";
    document.getElementById("backdrop-first").style.display = "none";
})

// view list button
const view_list_buttons = document.querySelectorAll(".view-list-button");
const view_list_title = document.querySelector(".view-list-title");
const view_list_overlay = document.getElementById("view-list-overlay");
let currentListId = null; // Track which list is currently open

view_list_buttons.forEach(function(button) {
    button.addEventListener("click", function() {
        const listContainer = button.closest(".lists-container");
        const listName = listContainer?.querySelector(".list-header h2")?.textContent || "Default List Name";
        currentListId = listContainer?.dataset.listId;

        if (view_list_title) {
            view_list_title.textContent = listName;
        }
        if (view_list_overlay) {
            view_list_overlay.style.display = "flex";
        }

        document.getElementById("backdrop-first").style.display = "block";
    });
})

// validate delete button
const validate_delete_button = document.getElementById("permanent-delete-list-button");
const delete_list_id_input = document.getElementById("delete-list-id");
const validate_delete_overlay = document.getElementById("validate-delete-overlay");

validate_delete_button.addEventListener("click", function() {
    if (delete_list_id_input && currentListId) {
        delete_list_id_input.value = currentListId;
    }

    // hide popup
    validate_delete_overlay.style.display = "none";
    document.getElementById("backdrop-second").style.display = "none";
});

// close list button
const close_list_button = document.getElementById("close-list-button");
close_list_button.addEventListener("click", function() {
    // get rid of popup and do nothing
    document.getElementById("view-list-overlay").style.display = "none";
    document.getElementById("backdrop-first").style.display = "none";
    currentListId = null;
})

// delete list button
const delete_list_button = document.getElementById("delete-list-button");
delete_list_button.addEventListener("click", function() {
    // show "are you sure" popup 
    document.getElementById("validate-delete-overlay").style.display = "flex";
    document.getElementById("backdrop-second").style.display = "block";
})

// cancel delete list action button
const cancel_delete_button = document.getElementById("cancel-delete-button");
cancel_delete_button.addEventListener("click", function() {
    // get rid of "are you sure" popup 
    document.getElementById("validate-delete-overlay").style.display = "none";
    document.getElementById("backdrop-second").style.display = "none";
})
