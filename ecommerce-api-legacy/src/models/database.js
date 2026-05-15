const sqlite3 = require('sqlite3').verbose();
const config = require('../config');
const { hashPassword } = require('../utils/crypto');

let db;

function getDb() {
    if (!db) {
        db = new sqlite3.Database(config.DB_PATH);
    }
    return db;
}

const run = (sql, params = []) => new Promise((resolve, reject) => {
    getDb().run(sql, params, function (err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
    });
});

const get = (sql, params = []) => new Promise((resolve, reject) => {
    getDb().get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
    });
});

const all = (sql, params = []) => new Promise((resolve, reject) => {
    getDb().all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
    });
});

async function initSchema() {
    await run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        pass TEXT NOT NULL
    )`);
    await run(`CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price REAL NOT NULL,
        active INTEGER DEFAULT 1
    )`);
    await run(`CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL
    )`);
    await run(`CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL
    )`);
    await run(`CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        created_at DATETIME DEFAULT (datetime('now'))
    )`);
}

async function seedIfEmpty() {
    const row = await get('SELECT COUNT(*) AS count FROM users');
    if (row.count > 0) return;

    await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
        'Leonan', 'leonan@fullcycle.com.br', hashPassword('123'),
    ]);
    await run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)', ['Clean Architecture', 997.00, 1]);
    await run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)', ['Docker', 497.00, 1]);
    await run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
    await run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [1, 997.00, 'PAID']);
}

module.exports = { run, get, all, initSchema, seedIfEmpty };
