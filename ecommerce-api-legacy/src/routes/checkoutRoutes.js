const express = require('express');
const router = express.Router();
const checkoutController = require('../controllers/checkoutController');

router.post('/checkout', async (req, res, next) => {
    const { usr: username, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

    if (!username || !email || !courseId || !cardNumber) {
        return res.status(400).json({ error: 'Bad Request: campos obrigatórios ausentes (usr, eml, c_id, card)' });
    }

    try {
        const result = await checkoutController.checkout({ username, email, password, courseId, cardNumber });
        res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (err) {
        next(err);
    }
});

module.exports = router;
