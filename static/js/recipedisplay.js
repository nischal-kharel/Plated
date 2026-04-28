// js for recipe view page
const page = document.querySelector('.recipe-page');
const recipeId = Number(page.dataset.recipeId);
const userRating = Number(page.dataset.userRating);
const prepTime = Number(page.dataset.prepTime);
const cookTime = Number(page.dataset.cookTime);
const servings = Number(page.dataset.servings);
const currentUserId = page.dataset.currentUser ? Number(page.dataset.currentUser) : null;
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
function toggleFavorite() {
    fetch('/recipe/' + recipeId + '/favorite', { method: 'POST' })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        var btn = document.getElementById('favBtn');
        btn.textContent = data.favorited ? '★ Favorited' : '☆ Favorite';
    });
}
// ── Reviews ──
const REVIEW_FULL = "/static/media/ratingimages/fullplate.png";
const REVIEW_HALF = "/static/media/ratingimages/leftbrokenplate.png";
let composeRating = 0;
let currentSort = 'recent';

function drawComposePlates(val) {
    var box = document.getElementById('composeRating');
    box.innerHTML = '';
    for (var i = 1; i <= 5; i++) {
        var img = document.createElement('img');
        if (val >= i)            { img.src = REVIEW_FULL; img.style.opacity = '1'; }
        else if (val >= i - 0.5) { img.src = REVIEW_HALF; img.style.opacity = '1'; }
        else                     { img.src = REVIEW_FULL; img.style.opacity = '0.25'; }
        img.setAttribute('data-index', i);
        box.appendChild(img);
    }
}
drawComposePlates(0);

// ── Review Tags ──
var reviewTags = [];

function drawReviewTags() {
    var box = document.getElementById('reviewTagBox');
    var input = document.getElementById('reviewTagInput');
    var existing = box.getElementsByClassName('review-tag');
    while (existing.length > 0) existing[0].parentNode.removeChild(existing[0]);

    for (var i = 0; i < reviewTags.length; i++) {
        var span = document.createElement('span');
        span.className = 'review-tag';
        span.innerHTML = reviewTags[i] + ' <span class="review-tag-remove" data-i="' + i + '">×</span>';
        box.insertBefore(span, input);
    }
    input.placeholder = reviewTags.length > 0 ? '' : 'e.g. delicious, spicy';
}

document.getElementById('reviewTagInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        var val = this.value.trim();
        if (val && reviewTags.indexOf(val) === -1) {
            reviewTags.push(val);
            drawReviewTags();
        }
        this.value = '';
    }
});

document.getElementById('reviewTagBox').addEventListener('click', function(e) {
    if (e.target.className === 'review-tag-remove') {
        reviewTags.splice(Number(e.target.getAttribute('data-i')), 1);
        drawReviewTags();
    }
});

document.getElementById('composeRating').addEventListener('mousemove', function(e) {
    if (e.target.tagName === 'IMG') {
        var i = Number(e.target.getAttribute('data-index'));
        drawComposePlates(e.offsetX < e.target.width / 2 ? i - 0.5 : i);
    }
});
document.getElementById('composeRating').addEventListener('mouseleave', function() {
    drawComposePlates(composeRating);
});
document.getElementById('composeRating').addEventListener('click', function(e) {
    if (e.target.tagName === 'IMG') {
        var i = Number(e.target.getAttribute('data-index'));
        composeRating = e.offsetX < e.target.width / 2 ? i - 0.5 : i;
        drawComposePlates(composeRating);
        document.getElementById('composeRatingText').textContent = composeRating + ' / 5';
    }
});

document.getElementById('writeReviewBtn').addEventListener('click', function() {
    document.getElementById('reviewOverlay').style.display = 'flex';
});
document.getElementById('cancelReview').addEventListener('click', function() {
    document.getElementById('reviewOverlay').style.display = 'none';
});

// close on backdrop click
document.getElementById('reviewOverlay').addEventListener('click', function(e) {
    if (e.target === this) {
        this.style.display = 'none';
    }
});

document.getElementById('reviewBody').addEventListener('input', function() {
    document.getElementById('charCount').textContent = this.value.length + ' / 1000';
});

document.getElementById('submitReview').addEventListener('click', function() {
    var body = document.getElementById('reviewBody').value.trim();
    if (!body) { alert('Please write something before posting.'); return; }
    fetch('/recipe/' + recipeId + '/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ body: body, score: composeRating || null })
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) {
            document.getElementById('reviewOverlay').style.display = 'none';
            document.getElementById('reviewBody').value = '';
            document.getElementById('composeRatingText').textContent = '';
            composeRating = 0;
            drawComposePlates(0);
            reviewTags = [];
            drawReviewTags();
            loadReviews(currentSort);
        } else {
            alert(data.error || 'Something went wrong.');
        }
    });
});

function renderStars(score) {
    var html = '';
    for (var i = 1; i <= 5; i++) {
        if (score >= i)          html += '<img src="' + REVIEW_FULL + '" style="width:14px;opacity:0.9">';
        else if (score >= i-0.5) html += '<img src="' + REVIEW_HALF + '" style="width:14px;opacity:0.9">';
        else                     html += '<img src="' + REVIEW_FULL + '" style="width:14px;opacity:0.2">';
    }
    return html;
}

function loadReviews(sort) {
    currentSort = sort;
    fetch('/recipe/' + recipeId + '/reviews?sort=' + sort)
    .then(function(res) { return res.json(); })
    .then(function(data) {
        var list = document.getElementById('reviewList');
        if (!data.reviews || data.reviews.length === 0) {
            list.innerHTML = '<p class="review-empty">No reviews yet. Be the first!</p>';
            return;
        }
        list.innerHTML = data.reviews.map(function(r) {
            var avatar = r.profile_pic
                ? '/static/' + r.profile_pic
                : '/static/media/profileimages/default-pfp.svg';
            var stars = r.score ? renderStars(r.score) : '';
            var isOwn = currentUserId && r.user_id === currentUserId;
            var likeBtn = !isOwn
                ? '<button class="review-like-btn ' + (r.user_liked ? 'liked' : '') + '" onclick="toggleReviewLike(' + r.review_id + ', this)">' +
                  (r.user_liked ? '♥' : '♡') + ' ' + r.like_count + '</button>'
                : '';
            return '<div class="review-card">' +
                '<a href="/profile/' + r.user_id + '">' +
                '<img src="' + avatar + '" class="review-avatar" alt="' + r.username + '">' +
                '</a>' +
                '<div class="review-content">' +
                '<div class="review-meta">' +
                '<a href="/profile/' + r.user_id + '" class="review-username">' + r.username + '</a>' +
                '<div class="review-score">' + stars + '</div>' +
                '<span class="review-date">' + r.created_at + '</span>' +
                '</div>' +
                '<p class="review-body">' + r.body + '</p>' +
                likeBtn +
                '</div>' +
                '</div>';
        }).join('');
    });
}

function toggleReviewLike(reviewId, btn) {
    fetch('/review/' + reviewId + '/like', { method: 'POST' })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) {
            var count = parseInt(btn.textContent.replace(/\D/g, ''));
            btn.classList.toggle('liked', data.liked);
            btn.textContent = (data.liked ? '♥ ' : '♡ ') + (data.liked ? count + 1 : count - 1);
        }
    });
}

document.querySelectorAll('.review-tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.review-tab').forEach(function(t) { t.classList.remove('active'); });
        tab.classList.add('active');
        loadReviews(tab.getAttribute('data-sort'));
    });
});

loadReviews('recent');