import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema, moveToTrashItemSchema, renameItemSchema } from '$lib/schemas/storage';
import type { Actions } from '@sveltejs/kit';
import {
	storageAvailableSpaceGet,
	storageFolderIdPost,
	storageFolderRootGet,
	storageMoveToTrashFileFileIdPatch,
	storageRenameFileFileIdPatch,
	storageRenameFolderFolderIdPatch,
	storageSuggestedFilesGet,
	storageSuggestedFoldersGet
} from '$lib/client';
import { handleFormResponse } from '$lib/utilities/actions';

export const load: PageServerLoad = async ({ cookies, parent, depends }) => {
	depends('data:home');

	const token = cookies.get('access_token');
	const root = (await parent()).root;

	const suggestedFoldersPromise = storageSuggestedFoldersGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const suggestedFilesPromise = storageSuggestedFilesGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const availableSpacePromise = storageAvailableSpaceGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const [{ data: suggestedFolders }, { data: suggestedFiles }, { data: availableSpace }] =
		await Promise.all([suggestedFoldersPromise, suggestedFilesPromise, availableSpacePromise]);

	return {
		suggestedFolders,
		suggestedFiles,
		folderId: root!.id,
		availableSpace,
		createFolderForm: await superValidate(zod4(createFolderSchema)),
		renameItemForm: await superValidate(zod4(renameItemSchema)),
	};
};

export const actions: Actions = {
	createFolder: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(createFolderSchema));
		const token = cookies.get('access_token');

		if (!form.valid) {
			return fail(400, { form });
		}

		const { data: root } = await storageFolderRootGet({
			headers: {
				Authorization: `Bearer ${token}`
			},
			throwOnError: true
		});

		const { name } = form.data;
		const { data, error } = await storageFolderIdPost({
			headers: {
				Authorization: `Bearer ${token}`
			},
			path: {
				folder_id: root.id
			},
			body: {
				name
			}
		});

		return handleFormResponse(form, data, error);
	},
	renameFolder: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(renameItemSchema));
		const token = cookies.get('access_token');

		if (!form.valid) {
			return fail(400, { form });
		}

		const { name, itemId: folderId } = form.data;
		const { data, error } = await storageRenameFolderFolderIdPatch({
			headers: {
				Authorization: `Bearer ${token}`
			},
			path: {
				folder_id: folderId
			},
			body: {
				name
			}
		});

		return handleFormResponse(form, data, error);
	},
	renameFile: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(renameItemSchema));
		const token = cookies.get('access_token');

		if (!form.valid) {
			return fail(400, { form });
		}

		const { name, itemId: fileId } = form.data;
		const { data, error } = await storageRenameFileFileIdPatch({
			headers: {
				Authorization: `Bearer ${token}`
			},
			path: {
				file_id: fileId
			},
			body: {
				name
			}
		});

		return handleFormResponse(form, data, error);
	}
};
