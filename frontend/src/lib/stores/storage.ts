import type { AvailableSpace, FolderPublic } from '$lib/client';
import { writable } from 'svelte/store';

export const storagePath = writable<FolderPublic[]>([]);
export const availableSpace = writable<AvailableSpace>();