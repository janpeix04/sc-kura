export type FieldName = 'firstName' | 'lastName' | 'email' | 'password';

type FeedbackType = 'error' | 'warning' | 'success' | null;
export interface PasswordFeedback {
	type: FeedbackType;
	message: string;
	tips?: string[];
}

export enum ORIGINS {
	Signup = 'signup',
	ResetPassword = 'resetPassword'
}

export type SortKeys = 'name' | 'owner' | 'date_modified' | 'size';

export type Mode = 'storage' | 'delete';
