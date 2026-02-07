import { z } from 'zod';

export const signupSchema = z.object({
    username: z.string().min(2, 'Username must be at least 2 character(s)'),
    email: z.email('Please enter a valid email'),
    password: z.string().min(8, 'Password must be at least 8 character(s)'),
    'confirm-password': z.string().min(8, 'Password confirm is required')
}).refine(data => data.password === data['confirm-password'], {
    message: "Password doesn't match",
    path: ['confirm-password']
});

export const loginSchema = z.object({
    username: z.email('Please enter a valid email'),
    password: z.string().min(8, "Password must be at least 8 character(s)")
});

export const forgotPasswordSchema = z.object({
    email: z.email("Please enter a valid email")
});

export const resetPasswordSchema = z.object({
    password: z.string().min(8, 'Password must be at least 8 character(s)'),
    'password-confirm': z.string().min(8, 'Password confirm is required'),
}).refine(data => data.password === data['password-confirm'], {
    message: "Passowrd doesn't match",
    path: ["password-confirm"]
});

export type SignupSchema = typeof signupSchema;
export type LoginSchema = typeof loginSchema;
export type ForgotPasswordSchema = typeof forgotPasswordSchema;
export type ResetPasswordSchema = typeof resetPasswordSchema;