import { writable } from 'svelte/store';

type VaultState = {
	token: string | null;
	expiresAt: number | null;
	locked: boolean;
	initialized: boolean;
};

export const vault = writable<VaultState>({
	token: null,
	expiresAt: null,
	locked: true,
	initialized: false
});
