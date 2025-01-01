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

const msg = {
    to: process.env.RECIPIENTS_EMAIL,
    from: process.env.SENDER_EMAIL,
    subject: 'Liste des déclarations de double licences',
    text: 'Bonjour,\n\nVoici la liste des déclarations de double licence de la dernière semaine.\n\nCordialement,\n\nGuillaume Lemaître',
    html: '<p>Bonjour,\n\nVoici la liste des déclarations de double licence de la dernière semaine.\n\nCordialement,\n\nGuillaume Lemaître</p>',
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
