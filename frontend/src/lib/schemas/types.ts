export enum ORIGINS {
	Signup = 'signup',
	ResetPassword = 'resetPassword'
}

export interface CeleryResult {
	errors: string[];
	success_count: number;
	total_count: number;
	message: string;
}
