// js for recipe instructions page

let currentStep = 1;
let ingredients = [];
let stepCount = 0;

// move forward one slide
function goNext() {
    if (currentStep === 1) {
        if (!document.getElementById("recipeName").value.trim() ||
            !document.getElementById("prepTime").value ||
            !document.getElementById("cookTime").value ||
            !document.getElementById("servings").value) {
            alert("Please fill in all fields before continuing.");
            return;
        }
    }
    if (currentStep === 2) {
        let desc = document.getElementById("recipeDescription").value.trim();
        let words = desc.split(" ");
        let wordCount = 0;
        for (let i = 0; i < words.length; i++) {
            if (words[i] !== "") wordCount++;
        }
        if (wordCount < 10) {
            alert("Please write a description of at least 10 words.");
            return;
        }
    }
    if (currentStep === 3) {
    if (selectedMealTypes.length === 0) {
        alert("Please select at least one meal type.");
        return;
    }
    if (selectedDietary.length === 0) {
        alert("Please select at least one dietary option.");
        return;
    }
}
    currentStep = currentStep + 1;
    document.getElementById("sliderTrack").style.transform = "translateX(-" + ((currentStep - 1) * 20) + "%)";
    document.getElementById("stepIndicator").textContent = "Step " + currentStep + " of 5";
}

// move back one slide
function goBack() {
    currentStep = currentStep - 1;
    document.getElementById("sliderTrack").style.transform = "translateX(-" + ((currentStep - 1) * 20) + "%)";
    document.getElementById("stepIndicator").textContent = "Step " + currentStep + " of 5";
}

// add ingredient to list
function addIngredient() {
    let input = document.getElementById("ingredientInput");
    let val = input.value.trim();
    if (val === "") return;
    ingredients[ingredients.length] = val;
    input.value = "";
    drawIngredients();
}

// photo preview
document.getElementById("recipePhoto").addEventListener("change", function() {
    let file = this.files[0];
    if (file) {
        document.getElementById("previewImg").src = URL.createObjectURL(file);
        document.getElementById("previewImg").style.display = "block";
        document.querySelector(".upload-overlay").style.display = "none";
        document.querySelector(".upload-card").classList.add("has-image");
    }
});

// add ingredient on enter key
document.getElementById("ingredientInput").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        addIngredient();
    }
});

// draw ingredient items from the array
function drawIngredients() {
    let list = document.getElementById("ingredientList");
    if (ingredients.length === 0) {
        list.innerHTML = "<p class='empty-hint'>No ingredients added yet</p>";
        return;
    }
    list.innerHTML = "";
    for (let i = 0; i < ingredients.length; i++) {
        let item = document.createElement("div");
        item.className = "ingredient-item";
        item.innerHTML = ingredients[i] + ' <span class="remove-item" data-i="' + i + '">×</span>';
        list.appendChild(item);
    }
}

// remove ingredient when x is clicked
document.getElementById("ingredientList").addEventListener("click", function(e) {
    if (e.target.className === "remove-item") {
        let index = Number(e.target.getAttribute("data-i"));
        let newList = [];
        for (let i = 0; i < ingredients.length; i++) {
            if (i !== index) {
                newList[newList.length] = ingredients[i];
            }
        }
        ingredients = newList;
        drawIngredients();
    }
});

// remove a step and recount
function removeStep(el) {
    el.closest(".step-card").remove();
    stepCount = document.querySelectorAll(".step-card").length;
    // renumber remaining steps
    let cards = document.querySelectorAll(".step-card");
    for (let i = 0; i < cards.length; i++) {
        cards[i].querySelector(".step-number").textContent = "Step " + (i + 1);
    }
}

// add a new step card
function addStep() {
    stepCount = stepCount + 1;
    let card = document.createElement("div");
    card.className = "step-card";
    card.innerHTML =
        '<div class="step-card-header">' +
            '<span class="step-number">Step ' + stepCount + '</span>' +
            '<input type="text" class="step-title-input" placeholder="Step title...">' +
            '<span class="remove-step" onclick="removeStep(this)">×</span>' +
        '</div>' +
        '<textarea class="step-detail-input" placeholder="Describe this step..."></textarea>';
    document.getElementById("stepsContainer").appendChild(card);
}
// start with one step already there
addStep();

// map dropdown labels to integers for the database
const prepTimeMap  = { minimal: 10,  standard: 25, extensive: 45 };
const cookTimeMap  = { minimal: 15,  standard: 35, extensive: 75 };
const servingsMap  = { minimal: 2,   standard: 4,  extensive: 8  };

// collect step cards into an array of {title, detail}
function collectSteps() {
    let cards = document.querySelectorAll(".step-card");
    let steps = [];
    for (let i = 0; i < cards.length; i++) {
        let title = cards[i].querySelector(".step-title-input").value.trim();
        let detail = cards[i].querySelector(".step-detail-input").value.trim();
        steps.push({ title: title, detail: detail });
    }
    return steps;
}

// save recipe to database
function saveRecipe() {
    if (ingredients.length === 0) {
        alert("Please add at least one ingredient.");
        return;
    }

    let steps = collectSteps();
    let hasContent = false;
    for (let i = 0; i < steps.length; i++) {
        if (steps[i].detail !== "") { hasContent = true; break; }
    }
    if (!hasContent) {
        alert("Please describe at least one step.");
        return;
    }

    // format directions as plain text for the database
    let directions = "";
    for (let i = 0; i < steps.length; i++) {
        directions += "Step " + (i + 1);
        if (steps[i].title) directions += ": " + steps[i].title;
        directions += "\n" + steps[i].detail + "\n\n";
    }

    let prepVal = document.getElementById("prepTime").value;
    let cookVal = document.getElementById("cookTime").value;
    let servVal = document.getElementById("servings").value;

    let formData = new FormData();
    formData.append("recipe_name",        document.getElementById("recipeName").value.trim());
    formData.append("description",        document.getElementById("recipeDescription").value.trim());
    formData.append("prep_time",          prepTimeMap[prepVal]);
    formData.append("cook_time",          cookTimeMap[cookVal]);
    formData.append("servings",           servingsMap[servVal]);
    formData.append("meal_types",         selectedMealTypes.join(","));
    formData.append("dietary_preference", selectedDietary.join(","));
    formData.append("ingredients",        ingredients.join(", "));
    formData.append("directions",         directions.trim());

    let photoFile = document.getElementById("recipePhoto").files[0];
    if (photoFile) {
        formData.append("recipe_pic", photoFile);
    }

    fetch("/recipes/new", {
        method: "POST",
        body: formData
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) {
            window.location.href = "/home";
        } else {
            alert("Error saving recipe: " + data.error);
        }
    })
    .catch(function() {
        alert("Something went wrong. Please try again.");
    });
}

// chip toggle for meal type and dietary
let selectedMealTypes = [];
let selectedDietary = [];

document.getElementById("mealTypeGroup").addEventListener("click", function(e) {
    if (e.target.classList.contains("chip")) {
        let val = e.target.getAttribute("data-val");
        if (e.target.classList.contains("selected")) {
            e.target.classList.remove("selected");
            let newList = [];
            for (let i = 0; i < selectedMealTypes.length; i++) {
                if (selectedMealTypes[i] !== val) newList[newList.length] = selectedMealTypes[i];
            }
            selectedMealTypes = newList;
        } else {
            e.target.classList.add("selected");
            selectedMealTypes[selectedMealTypes.length] = val;
        }
    }
});

document.getElementById("dietaryGroup").addEventListener("click", function(e) {
    if (e.target.classList.contains("chip")) {
        let val = e.target.getAttribute("data-val");
        if (e.target.classList.contains("selected")) {
            e.target.classList.remove("selected");
            let newList = [];
            for (let i = 0; i < selectedDietary.length; i++) {
                if (selectedDietary[i] !== val) newList[newList.length] = selectedDietary[i];
            }
            selectedDietary = newList;
        } else {
            e.target.classList.add("selected");
            selectedDietary[selectedDietary.length] = val;
        }
    }
});