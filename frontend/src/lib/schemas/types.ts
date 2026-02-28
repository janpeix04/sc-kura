import type { Icon } from "@lucide/svelte";

export enum ORIGINS {
	Signup = 'signup',
	ResetPassword = 'resetPassword'
}

export enum STORAGE_LAYOUT {
	Grid2x2 = 'grid2x2',
	List = 'list'
}

export enum STORAGE_STATUS {
	UPLOADED = 'U',
	DELETED = 'D'
}

export type SidebarPlatform = { 
	name: string; 
	logo: typeof Icon; 
	plan: string; 
};

export type StorageSortKey = 'name' | 'size' | 'lastModified';
export type StorageMode = 'delete' | 'storage';
