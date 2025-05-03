-- Create Users Table
CREATE TABLE IF NOT EXISTS utenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_utente VARCHAR(8) NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password VARCHAR(12) NOT NULL
);

-- Create Recipes Table
CREATE TABLE IF NOT EXISTS ricette (
    nr INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    ingredienti TEXT NOT NULL,
    procedimento TEXT NOT NULL,
    utente_id INTEGER NOT NULL,
    FOREIGN KEY (utente_id) REFERENCES utenti(id) ON DELETE CASCADE
);

-- Create Comments Table
CREATE TABLE IF NOT EXISTS commenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_nr INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    commento TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_nr) REFERENCES ricette(nr) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES utenti(id) ON DELETE CASCADE
);

-- Create Votes Table
CREATE TABLE IF NOT EXISTS voti (
    recipe_nr INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    voto INTEGER NOT NULL,
    PRIMARY KEY (recipe_nr, user_id),
    FOREIGN KEY (recipe_nr) REFERENCES ricette(nr) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES utenti(id) ON DELETE CASCADE
);

-- Create Favorites Table
CREATE TABLE IF NOT EXISTS preferiti (
    utente_id INTEGER NOT NULL,
    recipe_nr INTEGER NOT NULL,
    PRIMARY KEY (utente_id, recipe_nr),
    FOREIGN KEY (utente_id) REFERENCES utenti(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_nr) REFERENCES ricette(nr) ON DELETE CASCADE
);
