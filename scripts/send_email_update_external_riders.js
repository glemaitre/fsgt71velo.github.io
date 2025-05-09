#! /usr/bin/env node

const sgMail = require('@sendgrid/mail');
const path = require('path');
const fs = require('fs');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

// Add validation for required environment variables
const { RECIPIENTS_EXTERNAL_EMAIL, SENDER_EMAIL } = process.env;
if (!RECIPIENTS_EXTERNAL_EMAIL || !SENDER_EMAIL) {
    console.error('Missing env variables: RECIPIENTS_EXTERNAL_EMAIL and/or SENDER_EMAIL');
    process.exit(1);
}

// Check if external riders folder exists
const ridersFolder = 'scratch/external_riders';
if (fs.existsSync(ridersFolder)) {
    const files = fs.readdirSync(ridersFolder);

    // Group files by rider ID
    const riderFiles = {};
    files.forEach(file => {
        const match = file.match(/rider_(\d+)/);
        if (match) {
            const riderId = match[1];
            if (!riderFiles[riderId]) {
                riderFiles[riderId] = {};
            }
            if (file.endsWith('.html')) {
                riderFiles[riderId].html = file;
            } else if (file.endsWith('.txt') && !file.includes('subject')) {
                riderFiles[riderId].text = file;
            } else if (file.includes('subject')) {
                riderFiles[riderId].subject = file;
            }
        }
    });

    // Send email for each rider
    for (const riderId in riderFiles) {
        const { html, text, subject } = riderFiles[riderId];

        if (html && text && subject) {
            const emailHtml = fs.readFileSync(path.join(ridersFolder, html), 'utf8');
            const emailText = fs.readFileSync(path.join(ridersFolder, text), 'utf8');
            const emailSubject = fs.readFileSync(path.join(ridersFolder, subject), 'utf8').trim();

            const msg = {
                to: RECIPIENTS_EXTERNAL_EMAIL.split(',').map(email => email.trim()),
                from: SENDER_EMAIL.trim(),
                subject: emailSubject,
                text: emailText,
                html: emailHtml
            };

            sgMail
                .send(msg)
                .then(() => console.log(`Mail sent successfully for rider ${riderId}`))
                .catch(error => console.error(`Error sending mail for rider ${riderId}:`, error.toString()));
        }
    }
}
