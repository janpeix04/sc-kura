import { passwordStrength } from 'check-password-strength';

export function checkPasswordStrength(password: string) {
	return passwordStrength(password);
}
