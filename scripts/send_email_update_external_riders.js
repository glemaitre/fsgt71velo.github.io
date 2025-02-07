#! /usr/bin/env node

const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const fs = require('fs'),
    filename = 'scratch/update_external_riders_declaration.csv',
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
const { RECIPIENTS_EXTERNAL_EMAIL, SENDER_EMAIL } = process.env;
if (!RECIPIENTS_EXTERNAL_EMAIL || !SENDER_EMAIL) {
    console.error('Missing env variables: RECIPIENTS_EXTERNAL_EMAIL and/or SENDER_EMAIL');
    process.exit(1);
}

const emailText = 'Bonjour,\n\n' +
    'Voici la liste des enregistrements des coureurs extérieurs de la journée.\n\n' +
    'Cordialement,\n\n' +
    'Guillaume Lemaître';

const emailHtml = `
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p>Bonjour,</p>
        <p>Voici la liste des enregistrements des coureurs extérieurs de la journée.</p>
        <p>
            Cordialement,<br>
            Guillaume Lemaître
        </p>
    </div>
`;

const msg = {
    to: RECIPIENTS_EXTERNAL_EMAIL.split(',').map(email => email.trim()),
    from: SENDER_EMAIL.trim(),
    subject: 'Liste des enregistrements des coureurs extérieurs',
    text: emailText,
    html: emailHtml,
    attachments: [{
        content: data.toString('base64'),
        filename: filename,
        type: fileType,
        disposition: 'attachment'
    }]
};

sgMail
    .send(msg)
    .then(() => console.log('Mail sent successfully'))
    .catch(error => console.error(error.toString()));
