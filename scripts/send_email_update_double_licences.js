#! /usr/bin/env node

const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const fs = require('fs'),
    filename = 'scratch/update_double_licences_declaration.csv',
    fileType = 'text/csv';

if (!fs.existsSync(filename)) {
    console.log('No CSV file found - nothing to process');
    process.exit(0);
}

const data = fs.readFileSync(filename);
if (data.length === 0) {
    console.log('CSV file is empty - nothing to process');
    process.exit(0);
}

// Add validation for required environment variables
if (!process.env.RECIPIENTS_EMAIL || !process.env.SENDER_EMAIL) {
    console.error('Missing required environment variables: RECIPIENTS_EMAIL and/or SENDER_EMAIL');
    process.exit(1);
}

const msg = {
    to: process.env.RECIPIENTS_EMAIL.split(',').map(email => email.trim()),
    from: process.env.SENDER_EMAIL.trim(),
    subject: 'Liste des déclarations de double licences',
    text: 'Bonjour,\n\nVoici la liste des déclarations de double licence de la dernière semaine.\n\nCordialement,\n\nGuillaume Lemaître',
    html: '<p>Bonjour,<br><br>Voici la liste des déclarations de double licence de la dernière semaine.<br><br>Cordialement,<br><br>Guillaume Lemaître</p>',
    attachments: [
        {
            content: data.toString('base64'),
            filename: filename,
            type: fileType,
            disposition: 'attachment',
        },
    ],
};

sgMail
    .send(msg)
    .then(() => console.log('Mail sent successfully'))
    .catch(error => console.error(error.toString()));