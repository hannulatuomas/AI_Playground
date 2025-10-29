import { MailerSend, EmailParams, Sender, Recipient } from 'mailersend';
import dotenv from 'dotenv';

dotenv.config();

const mailerSend = new MailerSend({ apiKey: process.env.MAILERSEND_API_KEY! });
const sender = new Sender(process.env.MAILERSEND_SENDER_EMAIL!, 'SaaS App');

export async function sendVerificationEmail(to: string, token: string) {
  const verifyUrl = `${process.env.CLIENT_URL}/verify-email?token=${token}`;
  const recipients = [new Recipient(to, to)];
  const emailParams = new EmailParams()
    .setFrom(sender)
    .setTo(recipients)
    .setSubject('Verify your email')
    .setText(`Please verify your email by clicking the following link: ${verifyUrl}`)
    .setHtml(`<p>Please verify your email by clicking the following link:</p><p><a href="${verifyUrl}">${verifyUrl}</a></p>`);
  try {
    await mailerSend.email.send(emailParams);
  } catch (err) {
    console.error('MailerSend sendVerificationEmail error:', err);
    throw err;
  }
}

export async function sendPasswordResetEmail(to: string, token: string) {
  const resetUrl = `${process.env.CLIENT_URL}/reset-password?token=${token}`;
  const recipients = [new Recipient(to, to)];
  const emailParams = new EmailParams()
    .setFrom(sender)
    .setTo(recipients)
    .setSubject('Reset your password')
    .setText(`You requested a password reset. Click the following link to set a new password: ${resetUrl}`)
    .setHtml(`<p>You requested a password reset. Click the link below to set a new password:</p><p><a href="${resetUrl}">${resetUrl}</a></p>`);
  try {
    await mailerSend.email.send(emailParams);
  } catch (err) {
    console.error('MailerSend sendPasswordResetEmail error:', err);
    throw err;
  }
}
