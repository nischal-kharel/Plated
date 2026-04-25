// js for recipe view page
const FULL = "/static/media/ratingimages/fullplate.png";
const HALF = "/static/media/ratingimages/leftbrokenplate.png";

let selectedRating = 0;

// draw plates with half-plate support
function drawPlates(displayValue) {
    let box = document.getElementById("plateRating");
    box.innerHTML = "";

    for (let i = 1; i <= 5; i++) {
        let src = FULL;
        let opacity = "0.25";
        if (displayValue >= i) {
            src = FULL;
            opacity = "1";
        } else if (displayValue >= i - 0.5) {
            src = HALF;
            opacity = "1";
        }

        let plate = document.createElement("img");
        plate.src = src;
        plate.style.opacity = opacity;
        plate.style.width = "32px";
        plate.style.cursor = "pointer";
        plate.setAttribute("data-index", i);
        box.appendChild(plate);
    }
}

drawPlates(userRating);
selectedRating = userRating;

// hover left half = half rating, right half = full
document.getElementById("plateRating").addEventListener("mousemove", function(e) {
    if (e.target.tagName === "IMG") {
        let i = Number(e.target.getAttribute("data-index"));
        let mouseX = e.offsetX;
        let halfWidth = e.target.width / 2;
        if (mouseX < halfWidth) {
            drawPlates(i - 0.5);
        } else {
            drawPlates(i);
        }
    }
});

document.getElementById("plateRating").addEventListener("mouseleave", function() {
    drawPlates(selectedRating);
});

// click to set rating
document.getElementById("plateRating").addEventListener("click", function(e) {
    if (e.target.tagName === "IMG") {
        let i = Number(e.target.getAttribute("data-index"));
        let mouseX = e.offsetX;
        let halfWidth = e.target.width / 2;
        if (mouseX < halfWidth) {
            selectedRating = i - 0.5;
        } else {
            selectedRating = i;
        }
        fetch("/rate/" + recipeId, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ score: selectedRating })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.success) {
                drawPlates(selectedRating);
                document.querySelector(".avg-rating strong").textContent = data.new_avg;
            }
        });
    }
});

// color badges based on values
function getBadgeColor(val, type) {
    if (type === "serv") {
        if (val <= 2) return "badge-blue";
        if (val <= 6) return "badge-purple";
        return "badge-red";
    }
    if (type === "prep") {
        if (val <= 10) return "badge-blue";
        if (val <= 25) return "badge-purple";
        return "badge-red";
    }
    if (type === "cook") {
        if (val <= 15) return "badge-blue";
        if (val <= 35) return "badge-purple";
        return "badge-red";
    }
}

// apply badge colors on load
document.getElementById("prepBadge").classList.add(getBadgeColor(prepTime, "prep"));
document.getElementById("cookBadge").classList.add(getBadgeColor(cookTime, "cook"));
document.getElementById("servBadge").classList.add(getBadgeColor(servings, "serv"));

// toggle like button
function toggleLike() {
    fetch("/like/" + recipeId, { method: "POST" })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        let btn = document.getElementById("likeBtn");
        btn.textContent = data.liked ? "♥ Liked" : "♡ Like";
    });
}