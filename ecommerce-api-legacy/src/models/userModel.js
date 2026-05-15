const { run, get } = require('./database');
const { hashPassword, verifyPassword } = require('../utils/crypto');

async function findByEmail(email) {
    return get('SELECT * FROM users WHERE email = ?', [email]);
}

async function findById(id) {
    return get('SELECT id, name, email FROM users WHERE id = ?', [id]);
}

async function create(name, email, password) {
    const pass = hashPassword(password);
    const result = await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, pass]);
    return result.lastID;
}

async function authenticate(email, password) {
    const user = await get('SELECT * FROM users WHERE email = ?', [email]);
    if (!user) return null;
    if (!verifyPassword(user.pass, password)) return null;
    return { id: user.id, name: user.name, email: user.email };
}

module.exports = { findByEmail, findById, create, authenticate };
