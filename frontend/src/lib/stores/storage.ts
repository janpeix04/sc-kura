import { writable } from "svelte/store";

export const currentStoragePath = writable<string>("-")