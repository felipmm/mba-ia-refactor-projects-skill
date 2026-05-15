const { run, all } = require('../models/database');

async function deleteUser(userId) {
    const enrollments = await all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
    const enrollmentIds = enrollments.map(e => e.id);

    if (enrollmentIds.length > 0) {
        const placeholders = enrollmentIds.map(() => '?').join(',');
        await run(`DELETE FROM payments WHERE enrollment_id IN (${placeholders})`, enrollmentIds);
    }
    await run('DELETE FROM enrollments WHERE user_id = ?', [userId]);

    const result = await run('DELETE FROM users WHERE id = ?', [userId]);
    if (result.changes === 0) {
        const err = new Error('Usuário não encontrado');
        err.status = 404;
        throw err;
    }

    return { message: 'Usuário e dados relacionados removidos com sucesso.' };
}

module.exports = { deleteUser };
