import { writable } from 'svelte/store';

export const currentStoragePath = writable<string>('-');
export const deleteStorageFolderId = writable<Record<string, string>>({});