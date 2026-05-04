import * as z from 'zod';

export const renameItemSchema = z.object({
	name: z.string(),
	itemId: z.string()
});

export const moveToTrashItemSchema = z.object({
	itemId: z.string()
});

export type RenameItemSchema = z.infer<typeof renameItemSchema>;
export type MoveToTrashItemSchema = z.infer<typeof moveToTrashItemSchema>;
