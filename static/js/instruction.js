// js for recipe instructions page

let currentStep = 1;
let ingredients = [];
let stepCount = 0;

// move forward one slide
function goNext() {
    // need user to select all drop downs to get to next step
    if (currentStep === 1) {
        if (!document.getElementById("prepTime").value ||
            !document.getElementById("cookTime").value ||
            !document.getElementById("servings").value) {
            alert("Please fill in all fields before continuing.");
            return;
        }
    }
    currentStep = currentStep + 1;
    document.getElementById("sliderTrack").style.transform = "translateX(-" + ((currentStep - 1) * 25) + "%)";
    document.getElementById("stepIndicator").textContent = "Step " + currentStep + " of 4";
}

// move back one slide
function goBack() {
    currentStep = currentStep - 1;
    document.getElementById("sliderTrack").style.transform = "translateX(-" + ((currentStep - 1) * 25) + "%)";
    document.getElementById("stepIndicator").textContent = "Step " + currentStep + " of 4";
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

// save
function saveRecipe() {
    console.log("Prep:", document.getElementById("prepTime").value);
    console.log("Cook:", document.getElementById("cookTime").value);
    console.log("Servings:", document.getElementById("servings").value);
    console.log("Dietary:", document.getElementById("dietary").value);
    console.log("Meal type:", document.getElementById("mealType").value);
    console.log("Ingredients:", ingredients);
}