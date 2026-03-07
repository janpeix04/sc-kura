import type { FolderPublic } from '$lib/client';
import { writable } from 'svelte/store';

export const storagePath = writable<FolderPublic[]>([]);