// upload profile pic
const profilePicInput = document.getElementById("profile-pic");
const profilePreview = document.getElementById("profile-preview");

if (profilePicInput && profilePreview) {
    profilePicInput.addEventListener("change", async function() {
        const file = this.files[0];
        if (!file) return;

        profilePreview.src = URL.createObjectURL(file);

        const formData = new FormData();
        formData.append("profile_pic", file);

        try {
            const response = await fetch("/profile/upload_picture", {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                profilePreview.src = result.profile_pic;
            } else {
                alert(result.error || "Could not upload profile picture.");
            }
        } catch (error) {
            alert("Something went wrong while uploading the profile picture.");
        }
    });
}

// shared elements
const backdrop = document.getElementById("backdrop");

// edit profile popup
const editButton = document.getElementById("edit-profile-button");
const saveButton = document.getElementById("save-profile-button");
const editOverlay = document.getElementById("edit-overlay");
const bioText = document.getElementById("bio-text");
const bio = document.getElementById("bio");

if (editButton) {
    editButton.addEventListener("click", function() {
        bioText.value = bio.textContent;
        editOverlay.style.display = "flex";
        backdrop.style.display = "block";
    });
}

if (saveButton) {
    saveButton.addEventListener("click", function() {
        bio.textContent = bioText.value;
        editOverlay.style.display = "none";
        backdrop.style.display = "none";
    });
}

// followers/following popup
const followersTrigger = document.getElementById("followers-trigger");
const followingTrigger = document.getElementById("following-trigger");
const usersOverlay = document.getElementById("users-overlay");
const usersPopupTitle = document.getElementById("users-popup-title");
const usersPopupList = document.getElementById("users-popup-list");
const closeUsersPopup = document.getElementById("close-users-popup");

const followersData = document.getElementById("followers-data");
const followingData = document.getElementById("following-data");
const profileOwnerData = document.getElementById("profile-owner-id");

const followers = followersData ? JSON.parse(followersData.textContent) : [];
const following = followingData ? JSON.parse(followingData.textContent) : [];
const profileOwnerId = profileOwnerData ? JSON.parse(profileOwnerData.textContent) : null;

function renderUsers(users, title) {
    usersPopupTitle.textContent = title;
    usersPopupList.innerHTML = "";

    if (!users || users.length === 0) {
        usersPopupList.innerHTML = `<p class="empty-users-message">No ${title.toLowerCase()} yet.</p>`;
        return;
    }

    users.forEach(user => {
        const userRow = document.createElement("div");
        userRow.classList.add("user-row");

        const leftSide = document.createElement("div");
        leftSide.classList.add("user-row-left");

        const profileLink = document.createElement("a");
        profileLink.classList.add("user-link");
        profileLink.textContent = user.username;

        if (user.is_current_user) {
            profileLink.href = "/profile";
        } else {
            profileLink.href = `/profile/${user.user_id}`;
        }

        leftSide.appendChild(profileLink);
        userRow.appendChild(leftSide);

        if (!user.is_current_user) {
            const form = document.createElement("form");
            form.method = "POST";

            const returnInput = document.createElement("input");
            returnInput.type = "hidden";
            returnInput.name = "return_profile_id";
            returnInput.value = profileOwnerId;
            form.appendChild(returnInput);

            const button = document.createElement("button");
            button.type = "submit";
            button.classList.add("popup-follow-btn");

            if (user.is_followed_by_current_user) {
                form.action = `/unfollow/${user.user_id}`;
                button.classList.add("following");
                button.textContent = "Following";
            } else {
                form.action = `/follow/${user.user_id}`;
                button.textContent = "Follow";
            }

            form.appendChild(button);
            userRow.appendChild(form);
        }

        usersPopupList.appendChild(userRow);
    });
}

function openUsersPopup(users, title) {
    renderUsers(users, title);
    usersOverlay.style.display = "flex";
    backdrop.style.display = "block";
}

function closeAllPopups() {
    if (editOverlay) {
        editOverlay.style.display = "none";
    }
    if (usersOverlay) {
        usersOverlay.style.display = "none";
    }
    if (backdrop) {
        backdrop.style.display = "none";
    }
}

if (followersTrigger) {
    followersTrigger.addEventListener("click", function() {
        openUsersPopup(followers, "Followers");
    });
}

if (followingTrigger) {
    followingTrigger.addEventListener("click", function() {
        openUsersPopup(following, "Following");
    });
}

if (closeUsersPopup) {
    closeUsersPopup.addEventListener("click", closeAllPopups);
}

if (backdrop) {
    backdrop.addEventListener("click", closeAllPopups);
}
