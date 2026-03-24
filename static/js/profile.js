// upload profile pic
document.getElementById("profile-pic").addEventListener("change", function() {
    let file = this.files[0];
    if (file) {
        document.getElementById("profile-preview").src = URL.createObjectURL(file);
    }
});

// edit profile button
const edit_button = document.getElementById("edit-profile-button");
edit_button.addEventListener("click", function() {
    // set textarea to current bio
    document.getElementById("bio-text").value = document.getElementById("bio").textContent;
    // show popup
    document.getElementById("edit-overlay").style.display = "flex";
    document.getElementById("backdrop").style.display = "block";
})

// save button
const save_button = document.getElementById("save-profile-button");
save_button.addEventListener("click", function() {
    // change bio
    document.getElementById("bio").textContent = document.getElementById("bio-text").value;
    document.getElementById("edit-overlay").style.display = "none";
    document.getElementById("backdrop").style.display = "none";
})
