import { m } from '$lib/paraglide/messages';
import * as z from 'zod';

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

export type LoginSchema = z.infer<typeof loginSchema>;
export type ForgotPasswordSchema = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordSchema = z.infer<typeof resetPasswordSchema>;
