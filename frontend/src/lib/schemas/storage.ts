import { m } from '$lib/paraglide/messages';
import * as z from 'zod';

export const createFolderSchema = z.object({
	name: z.string().default(m.untitled_folder())
});

export const renameItemSchema = z.object({
	name: z.string(),
	itemId: z.string()
})

export type CreateFolderSchema = z.infer<typeof createFolderSchema>;
export type RenameItemSchema = z.infer<typeof renameItemSchema>;
