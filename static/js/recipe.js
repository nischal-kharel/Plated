// js for recipe page
const FULL = "/static/media/ratingimages/fullplate.png";
const HALF = "/static/media/ratingimages/leftbrokenplate.png";

// placeholder average rating for now
let avgRating = 4.5;

// draws the average rating plates
function drawAveragePlates(displayValue) {
    let box = document.getElementById("avgPlateRating");
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
        plate.alt = "rating plate";
        box.appendChild(plate);
    }
}

// set text + draw plates
document.getElementById("avgRatingText").textContent = avgRating + " out of 5";
drawAveragePlates(avgRating);
