import { writable } from 'svelte/store';

export const publicKey = writable<CryptoKey | undefined>();
export const privateKey = writable<CryptoKey | undefined>();
