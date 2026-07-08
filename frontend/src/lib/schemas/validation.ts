// Constants
export const NAME_REGEX = /^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$/;
export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const MIN_PASSWORD_LENGTH = 8;

// Utils
export type Validator<T = string> = (value: T) => string | undefined;

export const required =
	(message: string): Validator =>
	(value) =>
		!value.trim() ? message : undefined;
export const pattern =
	(regex: RegExp, message: string): Validator =>
	(value) =>
		value.trim() && !regex.test(value.trim()) ? message : undefined;
export const minLength =
	(length: number, message: string): Validator =>
	(value) =>
		value.trim().length > 0 && value.trim().length < length ? message : undefined;

export type ValidatorMap<T extends string> = Record<T, Validator[]>;

export function validateField<T extends string>(
	filed: T,
	value: string,
	validators: ValidatorMap<T>
): string | undefined {
	for (const validator of validators[filed]) {
		const error = validator(value);
		if (error) return error;
	}

	return undefined;
}

export function validateForm<T extends string>(
	values: Record<T, string>,
	validators: ValidatorMap<T>
): Record<T, string | undefined> {
	const errors = {} as Record<T, string | undefined>;

	for (const field of Object.keys(validators) as T[]) {
		errors[field] = validateField(field, values[field], validators);
	}

	return errors;
}
