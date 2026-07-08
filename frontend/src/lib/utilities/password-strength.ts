import { m } from '$lib/paraglide/messages';
import type { PasswordFeedback } from '$lib/schemas/types';
import { passwordStrength } from 'check-password-strength';

// Constants
export const PASSWORD_TIPS = [
	m.upper_and_lower_case_letters(),
	m.at_least_one_number_or_special_character()
];

export const STRENGTH_FEEDBACK: Record<number, Omit<PasswordFeedback, 'tips'>> = {
	0: { type: 'error', message: m.password_too_weak() },
	1: {
		type: 'warning',
		message: m.password_good_enough()
	},
	2: { type: 'success', message: m.password_medium_strength() },
	3: { type: 'success', message: m.password_strong() }
};

// Utils
export function checkPasswordStrength(password: string) {
	return passwordStrength(password);
}
