export type FormErrors = {
	firstName?: string;
	lastName?: string;
	email?: string;
	password?: string;
};

export enum ORIGINS {
	Signup = 'signup',
	ResetPassword = 'resetPassword'
}

export type SortKeys = 'name' | 'owner' | 'date_modified' | 'size';

export type Mode = 'storage' | 'delete';
