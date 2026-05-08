export enum ORIGINS {
	Signup = 'signup',
	ResetPassword = 'resetPassword'
}

export type SortKeys = 'name' | 'owner' | 'date_modified' | 'size' | 'date_created' | 'type';

export type Mode = 'storage' | 'delete';

export type DecryptedFolder = {
	id: string;
	key: CryptoKey;
	name: string;
	type: string;
	size: number;
	createdAt: string;
	parentId: string | null;
};

export type DecryptedFile = {
	id: string;
	key: CryptoKey;
	name: string;
	type: string;
	size: number;
	createdAt: string;
	parentId: string;
};

export type DecryptedBreadcrumb = {
	folder_id: string;
	name: string;
};

export type DecryptedFileNode = {
	id: string;
	name: string;
	blob: Blob;
};

export type DecryptedFolderNode = {
	id: string;
	name: string;
	folders: DecryptedFolderNode[];
	files: DecryptedFileNode[];
};
