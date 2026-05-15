const { run, get, all } = require('./database');

async function create(enrollmentId, amount, status) {
    const result = await run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, amount, status]
    );
    return result.lastID;
}

async function findByEnrollmentId(enrollmentId) {
    return get('SELECT * FROM payments WHERE enrollment_id = ?', [enrollmentId]);
}

async function deleteByEnrollmentIds(enrollmentIds) {
    if (enrollmentIds.length === 0) return;
    const placeholders = enrollmentIds.map(() => '?').join(',');
    return run(`DELETE FROM payments WHERE enrollment_id IN (${placeholders})`, enrollmentIds);
}

module.exports = { create, findByEnrollmentId, deleteByEnrollmentIds };
