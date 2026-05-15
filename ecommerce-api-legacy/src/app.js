const express = require('express');
const config = require('./config');
const { initSchema, seedIfEmpty } = require('./models/database');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

async function createApp() {
    await initSchema();
    await seedIfEmpty();

    const app = express();
    app.use(express.json());

    app.use('/api', checkoutRoutes);
    app.use('/api', reportRoutes);
    app.use('/api', userRoutes);

    app.use(errorHandler);

    return app;
}

if (require.main === module) {
    createApp()
        .then(app => {
            app.listen(config.PORT, () => {
                console.log(`LMS API rodando na porta ${config.PORT}...`);
            });
        })
        .catch(err => {
            console.error('Falha ao iniciar:', err);
            process.exit(1);
        });
}

module.exports = { createApp };
