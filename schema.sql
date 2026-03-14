-- ============================================
-- PLATED - Database Schema
-- CS 1530 Software Engineering - Spring 2026
-- ============================================
-- SETUP: Run these commands in your MySQL terminal
--   Open MySQL
--   Copy the contents of this file in "Query1" and execute
--   Refresh all schema tables 
-- ============================================

CREATE DATABASE IF NOT EXISTS plated;
USE plated;

-- ============================================
-- USERS
-- Combines User + Profile from the class diagram
-- (1:1 composition, so one table is cleaner).
-- ============================================
CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(20)  NOT NULL UNIQUE,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name  VARCHAR(100),
    bio           TEXT,
    profile_pic   VARCHAR(255),
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================
-- FOLLOWS
-- Self-referencing many-to-many relationship with users.
-- follower_id follows following_id.
-- follower_id and following_id reference users.user_id
-- ============================================
CREATE TABLE follows (
    follower_id  INT NOT NULL,
    following_id INT NOT NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id)  REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CHECK (follower_id <> following_id)
);

-- ============================================
-- RECIPES
-- ============================================
CREATE TABLE recipes (
    recipe_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT          NOT NULL,
    recipe_name  VARCHAR(255) NOT NULL,
    description  TEXT,
    ingredients  TEXT         NOT NULL,
    directions   TEXT         NOT NULL,
    recipe_pic   VARCHAR(255),
    view_count   INT          NOT NULL DEFAULT 0,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================
-- JOURNAL POSTS (Food Journal)
-- Rating is set by the post creator only.
-- Supports half-star increments (0.5 to 5.0).
-- ============================================
CREATE TABLE journal_posts (
    journal_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT          NOT NULL,
    journal_name VARCHAR(255) NOT NULL,
    caption      TEXT,
    journal_pic  VARCHAR(255),
    rating       DECIMAL(2,1) CHECK (rating BETWEEN 0.5 AND 5.0 AND rating * 2 = FLOOR(rating * 2)),
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================
-- TAGS
-- Shared tag pool used by both recipes and
-- journal posts via junction tables below.
-- ============================================
CREATE TABLE tags (
    tag_id   INT AUTO_INCREMENT PRIMARY KEY,
    tag_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE recipe_tags (
    recipe_id INT NOT NULL,
    tag_id    INT NOT NULL,
    PRIMARY KEY (recipe_id, tag_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)    REFERENCES tags(tag_id)        ON DELETE CASCADE
);

CREATE TABLE journal_tags (
    journal_id INT NOT NULL,
    tag_id     INT NOT NULL,
    PRIMARY KEY (journal_id, tag_id),
    FOREIGN KEY (journal_id) REFERENCES journal_posts(journal_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)     REFERENCES tags(tag_id)              ON DELETE CASCADE
);

-- ============================================
-- RECIPE RATINGS
-- One rating per user per recipe.
-- Supports half-star increments (0.5 to 5.0).
-- ============================================
CREATE TABLE recipe_ratings (
    user_id    INT          NOT NULL,
    recipe_id  INT          NOT NULL,
    score      DECIMAL(2,1) NOT NULL CHECK (score BETWEEN 0.5 AND 5.0 AND score * 2 = FLOOR(score * 2)),
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id)   REFERENCES users(user_id)     ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE
);

-- ============================================
-- LIKES
-- Separate tables for recipe and journal likes.
-- ============================================
CREATE TABLE recipe_likes (
    user_id    INT NOT NULL,
    recipe_id  INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id)   REFERENCES users(user_id)     ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE
);

CREATE TABLE journal_likes (
    user_id    INT NOT NULL,
    journal_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, journal_id),
    FOREIGN KEY (user_id)    REFERENCES users(user_id)            ON DELETE CASCADE,
    FOREIGN KEY (journal_id) REFERENCES journal_posts(journal_id) ON DELETE CASCADE
);

-- ============================================
-- COMMENTS
-- A comment targets either a recipe OR a journal post (never both).
-- The CHECK constraint enforces that exactly one FK is set.
-- ============================================
CREATE TABLE comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT  NOT NULL,
    recipe_id  INT  NULL,
    journal_id INT  NULL,
    body       TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(user_id)            ON DELETE CASCADE,
    FOREIGN KEY (recipe_id)  REFERENCES recipes(recipe_id)        ON DELETE CASCADE,
    FOREIGN KEY (journal_id) REFERENCES journal_posts(journal_id) ON DELETE CASCADE,
    CHECK (
        (recipe_id IS NOT NULL AND journal_id IS NULL) OR
        (recipe_id IS NULL     AND journal_id IS NOT NULL)
    )
);

-- ============================================
-- FAVORITE RECIPES (bookmarks / saved list)
-- ============================================
CREATE TABLE favorite_recipes (
    user_id    INT NOT NULL,
    recipe_id  INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id)   REFERENCES users(user_id)     ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE
);

-- ============================================
-- INDEXES (for performance on common queries)
-- ============================================

-- show me all recipes by user X, newest first (Useful for profile page)
CREATE INDEX idx_recipes_user_created  ON recipes(user_id, created_at DESC);

-- show me all journal posts by user X, newest first (Useful for profile page)
CREATE INDEX idx_journals_user_created ON journal_posts(user_id, created_at DESC);

--sort recipes by view_count ("Popular Recipes List")
CREATE INDEX idx_recipes_views         ON recipes(view_count DESC);

-- When user searches by tag
CREATE INDEX idx_tag_name              ON tags(tag_name);


-- Fulltext index for search bar functionality
-- "special type of index for text search.
-- It lets users type something like "chicken pasta" into the search bar
-- and MySQL will find recipes where those words appear anywhere in the
-- name, description, or ingredients."
ALTER TABLE recipes ADD FULLTEXT idx_recipe_search (recipe_name, description, ingredients);
