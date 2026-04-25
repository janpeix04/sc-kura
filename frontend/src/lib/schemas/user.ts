import * as z from 'zod';
import { nameRegex } from './auth';
import { m } from '$lib/paraglide/messages';

export const updateUserSchema = z.object({
	first_name: z.string().regex(nameRegex, m.valid_first_name()).optional(),
	last_name: z.string().regex(nameRegex, m.valid_last_name()).optional(),
	email: z.email(m.valid_email()).optional(),
	password: z.string().min(8, m.valid_password_length()).optional(),
	hasSeenPersonalVault: z.boolean().optional()
});

export type UpdateUserSchema = z.infer<typeof updateUserSchema>;
