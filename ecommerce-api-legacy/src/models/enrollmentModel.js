const { run, all } = require('./database');

async function create(userId, courseId) {
    const result = await run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, courseId]
    );
    return result.lastID;
}

async function findByCourseId(courseId) {
    return all('SELECT * FROM enrollments WHERE course_id = ?', [courseId]);
}

async function findByUserId(userId) {
    return all('SELECT * FROM enrollments WHERE user_id = ?', [userId]);
}

async function deleteByUserId(userId) {
    return run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
}

module.exports = { create, findByCourseId, findByUserId, deleteByUserId };
