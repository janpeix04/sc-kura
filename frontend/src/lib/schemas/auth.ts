import { m } from '$lib/paraglide/messages';
import * as z from 'zod';

// Allows:
// - Latin letters (a-z, A-Z)
// - Accents (é, ñ, ü, ç, etc.)
// - Cyrillic (А-Я, а-я)
// - No numbers or symbols
const nameRegex = /^[\p{L}]+$/u;

export const signupSchema = z
	.object({
		firstName: z
			.string()
			.min(2, m.valid_first_name_length())
			.regex(nameRegex, m.valid_first_name()),
		lastName: z.string().min(2, m.valid_last_name_length()).regex(nameRegex, m.valid_last_name()),
		email: z.email(m.valid_email()),
		password: z.string().min(8, m.valid_password_length()),
		confirmPassword: z.string().min(8, m.valid_password_length())
	})
	.refine((data) => data.password === data.confirmPassword, {
		message: m.password_mismatch(),
		path: ['confirmPassword']
	});

export const loginSchema = z.object({
	username: z.email(m.valid_email()),
	password: z.string().min(8, m.valid_password_length())
});

export const forgotPasswordSchema = z.object({
	email: z.email(m.valid_email())
});

export const resetPasswordSchema = z
	.object({
		password: z.string().min(8, m.valid_password_length()),
		confirmPassword: z.string().min(8, m.valid_password_length())
	})
	.refine((data) => data.password === data.confirmPassword, {
		message: m.password_mismatch(),
		path: ['confirmPassword']
	});

export type SignupSchema = z.infer<typeof signupSchema>;
export type LoginSchema = z.infer<typeof loginSchema>;
export type ForgotPasswordSchema = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordSchema = z.infer<typeof resetPasswordSchema>;
