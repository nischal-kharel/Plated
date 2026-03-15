// js for meal page
const FULL = "/static/media/ratingimages/fullplate.png";
const HALF = "/static/media/ratingimages/leftbrokenplate.png";

let rating = 0;
let tags = [];

// set today's date
let today = new Date();
document.getElementById("eatenDate").value = today.toISOString().split("T")[0];

// photo preview
document.getElementById("mealPhoto").addEventListener("change", function() {
    let file = this.files[0];
    if (file) {
        document.getElementById("previewImg").src = URL.createObjectURL(file);
        document.getElementById("previewImg").style.display = "block";
        document.querySelector(".upload-overlay").style.display = "none";
    }
});

// journal toggle
document.getElementById("addToJournal").addEventListener("change", function() {
    if (this.checked) {
        document.getElementById("addToJournalRow").classList.add("hidden");
        document.getElementById("journalDetail").classList.add("visible");
    }
});

document.getElementById("eatenCheck").addEventListener("change", function() {
    this.checked = true;
    document.getElementById("journalDetail").classList.remove("visible");
    document.getElementById("addToJournalRow").classList.remove("hidden");
    document.getElementById("addToJournal").checked = false;
});

// draws the 5 plates in the footer and the small ones next to date 
function drawPlates(displayValue) {
    let box = document.getElementById("pltratingBox");
    let mini = document.getElementById("miniRating");
    box.innerHTML = "";
    mini.innerHTML = "";

    for (let i = 1; i <= 5; i++) {
        // decide which image and opacity to use
        let src = FULL;
        let opacity = "0.25";
        if (displayValue >= i) {
            src = FULL;
            opacity = "1";
        } else if (displayValue >= i - 0.5) {
            src = HALF;
            opacity = "1";
        }

        // big plate for footer
        let plate = document.createElement("img");
        plate.src = src;
        plate.style.opacity = opacity;
        plate.style.width = "32px";
        plate.style.cursor = "pointer";
        plate.setAttribute("data-index", i);
        box.appendChild(plate);

        // small plate next to journal row
        let miniPlate = document.createElement("img");
        miniPlate.src = src;
        miniPlate.style.opacity = opacity;
        miniPlate.style.width = "20px";
        mini.appendChild(miniPlate);
    }
}

drawPlates(0);

// hover over left half of plate = half rating, right half = full
document.getElementById("pltratingBox").addEventListener("mousemove", function(e) {
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

document.getElementById("pltratingBox").addEventListener("mouseleave", function() {
    drawPlates(rating);
});

document.getElementById("pltratingBox").addEventListener("click", function(e) {
    if (e.target.tagName === "IMG") {
        let i = Number(e.target.getAttribute("data-index"));
        let mouseX = e.offsetX;
        let halfWidth = e.target.width / 2;
        if (mouseX < halfWidth) {
            rating = i - 0.5;
        } else {
            rating = i;
        }
        document.getElementById("pltratingText").textContent = rating + " out of 5";
        document.getElementById("pltratingClear").style.display = "inline";
        document.getElementById("miniRating").style.display = "flex";
        drawPlates(rating);
    }
});

// clear rating
document.getElementById("pltratingClear").addEventListener("click", function() {
    rating = 0;
    document.getElementById("pltratingText").textContent = "";
    document.getElementById("pltratingClear").style.display = "none";
    document.getElementById("miniRating").style.display = "none";
    drawPlates(0);
});

// draws the tag items from the tags array
function drawTags() {
    let box = document.getElementById("tagBox");
    let input = document.getElementById("tagInput");

    // remove all current tag items first
    let existingTags = document.getElementsByClassName("tag");
    while (existingTags.length > 0) {
        existingTags[0].parentNode.removeChild(existingTags[0]);
    }

    // add a new tag item for each tag in the array
    for (let i = 0; i < tags.length; i++) {
        let tagItem = document.createElement("span");
        tagItem.className = "tag";
        tagItem.innerHTML = tags[i] + ' <span class="remove" data-i="' + i + '">×</span>';
        box.insertBefore(tagItem, input);
    }
}

// add tag on enter
document.getElementById("tagInput").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        let val = this.value.trim();
        let alreadyExists = false;
        for (let i = 0; i < tags.length; i++) {
            if (tags[i] === val) {
                alreadyExists = true;
            }
        }
        if (val !== "" && alreadyExists === false) {
            tags[tags.length] = val;
            drawTags();
        }
        this.value = "";
    }
});

// remove tag when x is clicked
document.getElementById("tagBox").addEventListener("click", function(e) {
    if (e.target.className === "remove") {
        let index = Number(e.target.getAttribute("data-i"));
        let newTags = [];
        for (let i = 0; i < tags.length; i++) {
            if (i !== index) {
                newTags[newTags.length] = tags[i];
            }
        }
        tags = newTags;
        drawTags();
    }
});

// submit
document.getElementById("mealForm").addEventListener("submit", function(e) {
    e.preventDefault();
    console.log("Meal:", document.getElementById("mealTitle").value);
    console.log("Caption:", document.getElementById("mealCaption").value);
    console.log("Tags:", tags);
    console.log("Rating:", rating);
});