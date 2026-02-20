export enum ORIGINS {
	Signup = 'signup',
	ResetPassword = 'resetPassword'
}

export enum STORAGE_LAYOUT {
	Grid2x2 = 'grid2x2',
	List = 'list'
}

export type SidebarPlatform = { 
	name: string; 
	logo: any; 
	plan: string; 
	url: string;
};

export type StorageSortKey = 'name' | 'size' | 'lastModified';
