const courseModel = require('../models/courseModel');
const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const { run } = require('../models/database');

function processPayment(cardNumber) {
    // NOTE: replace with real gateway integration in production
    return cardNumber.startsWith('4') ? 'PAID' : 'DENIED';
}

async function checkout({ username, email, password, courseId, cardNumber }) {
    const course = await courseModel.findById(courseId);
    if (!course) {
        const err = new Error('Curso não encontrado');
        err.status = 404;
        throw err;
    }

    const paymentStatus = processPayment(cardNumber);
    if (paymentStatus === 'DENIED') {
        const err = new Error('Pagamento recusado');
        err.status = 400;
        throw err;
    }

    let user = await userModel.findByEmail(email);
    const userId = user
        ? user.id
        : await userModel.create(username, email, password || '123456');

    const enrollmentId = await enrollmentModel.create(userId, courseId);
    await paymentModel.create(enrollmentId, course.price, paymentStatus);
    await run(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [`Checkout curso ${courseId} por usuário ${userId}`]
    );

    return { enrollmentId };
}

module.exports = { checkout };
