const { all } = require('../models/database');

async function financialReport() {
    const rows = await all(`
        SELECT c.id        AS course_id,
               c.title     AS course_title,
               u.name      AS student_name,
               p.amount    AS paid_amount,
               p.status    AS payment_status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u       ON u.id = e.user_id
        LEFT JOIN payments p    ON p.enrollment_id = e.id
        ORDER BY c.id
    `);

    const coursesMap = {};
    for (const row of rows) {
        if (!coursesMap[row.course_id]) {
            coursesMap[row.course_id] = {
                course: row.course_title,
                revenue: 0,
                students: [],
            };
        }
        if (row.student_name) {
            if (row.payment_status === 'PAID') {
                coursesMap[row.course_id].revenue += row.paid_amount;
            }
            coursesMap[row.course_id].students.push({
                student: row.student_name,
                paid: row.paid_amount || 0,
            });
        }
    }

    return Object.values(coursesMap);
}

module.exports = { financialReport };
