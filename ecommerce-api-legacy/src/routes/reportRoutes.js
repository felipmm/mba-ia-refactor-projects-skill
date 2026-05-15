const express = require('express');
const router = express.Router();
const reportController = require('../controllers/reportController');

router.get('/admin/financial-report', async (req, res, next) => {
    try {
        const report = await reportController.financialReport();
        res.json(report);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
