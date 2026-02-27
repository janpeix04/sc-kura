import type { FileFolderPublic } from '$lib/client';
import { writable } from 'svelte/store';

export const currentStoragePath = writable<string>('-');
export const storagePath = writable<FileFolderPublic[]>([]);