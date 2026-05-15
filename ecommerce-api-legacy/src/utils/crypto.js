const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha256').toString('hex');
    return `${salt}:${hash}`;
}

function verifyPassword(stored, provided) {
    if (!stored || !stored.includes(':')) {
        return stored === provided;
    }
    const [salt, hash] = stored.split(':');
    const verify = crypto.pbkdf2Sync(provided, salt, 100000, 64, 'sha256').toString('hex');
    return hash === verify;
}

module.exports = { hashPassword, verifyPassword };
