import { m } from '$lib/paraglide/messages';
import { z } from 'zod';

export const loginSchema = z.object({
    username: z.email(m.valid_email()),
    password: z.string().min(8, m.valid_password_length())
});

export type LoginSchema = typeof loginSchema;