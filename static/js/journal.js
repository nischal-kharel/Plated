const FULL = "/static/media/ratingimages/fullplate.png";
const HALF = "/static/media/ratingimages/leftbrokenplate.png";

const mealPosts = document.querySelectorAll(".meal-post");
const modal = document.getElementById("meal-modal");
const backdrop = document.getElementById("modal-backdrop");
const closeModal = document.getElementById("close-modal");

const modalImage = document.getElementById("modal-image");
const modalTitle = document.getElementById("modal-title");
const modalRatingText = document.getElementById("modal-rating-text");
const modalRatingPlates = document.getElementById("modal-rating-plates");
const modalCaption = document.getElementById("modal-caption");
const modalTags = document.getElementById("modal-tags");
const deletePostBtn = document.getElementById("delete-post-btn");

let activeJournalId = null;

function drawModalPlates(ratingValue) {
    modalRatingPlates.innerHTML = "";

    if (!ratingValue) {
        return;
    }

    const rating = Number(ratingValue);

    for (let i = 1; i <= 5; i++) {
        const plate = document.createElement("img");

        if (rating >= i) {
            plate.src = FULL;
        } else if (rating >= i - 0.5) {
            plate.src = HALF;
        } else {
            plate.src = FULL;
            plate.style.opacity = "0.25";
        }

        modalRatingPlates.appendChild(plate);
    }
}

mealPosts.forEach(post => {
    post.addEventListener("click", function() {
        activeJournalId = post.dataset.id;
        modalImage.src = post.dataset.image;
        modalTitle.textContent = post.dataset.title || "Meal";

        if (post.dataset.rating) {
            modalRatingText.textContent = `${post.dataset.rating} out of 5`;
            drawModalPlates(post.dataset.rating);
        } else {
            modalRatingText.textContent = "No rating";
            modalRatingPlates.innerHTML = "";
        }

        modalCaption.textContent = post.dataset.caption || "No caption";
        modalTags.textContent = post.dataset.tags ? `Tags: ${post.dataset.tags}` : "No tags";

        modal.style.display = "block";
        backdrop.style.display = "block";
    });
});

function closePopup() {
    modal.style.display = "none";
    backdrop.style.display = "none";
    activeJournalId = null;
}

if (closeModal) {
    closeModal.addEventListener("click", closePopup);
}

if (backdrop) {
    backdrop.addEventListener("click", closePopup);
}

if (deletePostBtn) {
    deletePostBtn.addEventListener("click", async function() {
        if (!activeJournalId) return;

        const confirmed = confirm("Delete this meal post?");
        if (!confirmed) return;

        try {
            const response = await fetch(`/journal/delete/${activeJournalId}`, {
                method: "POST"
            });

            const result = await response.json();

            if (result.success) {
                window.location.reload();
            } else {
                alert(result.error || "Could not delete post.");
            }
        } catch (error) {
            alert("Something went wrong while deleting the post.");
        }
    });
}