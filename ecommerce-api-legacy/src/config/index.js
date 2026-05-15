module.exports = {
    PORT: process.env.PORT || 3000,
    DB_PATH: process.env.DB_PATH || 'lms.db',
    PAYMENT_GATEWAY_KEY: process.env.PAYMENT_GATEWAY_KEY || '',
    SMTP_USER: process.env.SMTP_USER || '',
};
