-- gestione_database.sql
-- Script per la creazione del database e delle tabelle per la gestione di utenti e ricette

-- 1. Creazione del database (se non esiste)
DROP DATABASE IF EXISTS gestioneRicette;
CREATE DATABASE gestioneRicette;
USE gestioneRicette;

-- 2. Creazione della tabella utenti
DROP TABLE IF EXISTS utenti;
CREATE TABLE utenti (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome_utente VARCHAR(8) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(12) NOT NULL
);

-- 3. Creazione della tabella ricette
DROP TABLE IF EXISTS ricette;
CREATE TABLE ricette (
    nr INT PRIMARY KEY AUTO_INCREMENT,
    ingredienti TEXT NOT NULL,
    procedimento TEXT NOT NULL,
    commenti TEXT,
    voto INT,
    utente_id INT NOT NULL,
    CONSTRAINT fk_ricette_utenti FOREIGN KEY (utente_id)
        REFERENCES utenti(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- 4. Creazione della tabella preferiti
-- Questa tabella permette di associare ad ogni utente una lista di ricette preferite
DROP TABLE IF EXISTS preferiti;
CREATE TABLE preferiti (
    utente_id INT NOT NULL,
    nr INT NOT NULL,
    PRIMARY KEY (utente_id, nr),
    CONSTRAINT fk_preferiti_utenti FOREIGN KEY (utente_id)
        REFERENCES utenti(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_preferiti_ricette FOREIGN KEY (nr)
        REFERENCES ricette(nr)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

