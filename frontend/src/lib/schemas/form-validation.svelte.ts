import { validateForm, type ValidatorMap } from './validation';

export function createFormValidator<T extends string>(validators: ValidatorMap<T>) {
	let errors: Record<T, string | undefined> = $state({} as Record<T, string | undefined>);

	function validate(values: Record<T, string>) {
		const result = validateForm(values, validators);

		errors = Object.fromEntries(Object.entries(result).filter(([, value]) => value)) as Record<
			T,
			string | undefined
		>;

		return Object.values(result).every((v) => !v);
	}

	function clearError(field: T) {
		if (errors[field]) {
			errors = {
				...errors,
				[field]: undefined
			};
		}
	}

	return {
		get errors() {
			return errors;
		},
		validate,
		clearError
	};
}
