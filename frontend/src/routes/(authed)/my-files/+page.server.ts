import {
	storageFolderIdPost,
	storageFoldersFolderIdGet,
	type FolderPublic,
	storageRenameFolderFolderIdPatch,
	storageFilesFolderIdGet,
	storageFolderRootGet,
	storageAvailableSpaceGet,
	storageRenameFileFileIdPatch,
	storageMoveToTrashFileFileIdPatch
} from '$lib/client';
import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema, moveToTrashItemSchema, renameItemSchema } from '$lib/schemas/storage';
import type { Actions } from '@sveltejs/kit';
import { handleFormResponse } from '$lib/utilities/actions';

export const load: PageServerLoad = async ({ cookies, parent, depends }) => {
	depends('data:my-files');

	const token = cookies.get('access_token');
	const root = (await parent()).root as FolderPublic;

	const foldersPromise = storageFoldersFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: root.id
		}
	});

	const filesPromise = storageFilesFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: root.id
		}
	});

	const availableSpacePromise = storageAvailableSpaceGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const [{ data: folders }, { data: files }, { data: availableSpace }] = await Promise.all([
		foldersPromise,
		filesPromise,
		availableSpacePromise
	]);

	return {
		folders,
		files,
		folderId: root!.id,
		availableSpace,
		createFolderForm: await superValidate(zod4(createFolderSchema)),
		renameItemForm: await superValidate(zod4(renameItemSchema)),
		moveToTrashItemForm: await superValidate(zod4(moveToTrashItemSchema))
	};
};

export const actions: Actions = {
	createFolder: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(createFolderSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const token = cookies.get('access_token');
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
	},
	moveToTrashFile: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(moveToTrashItemSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const token = cookies.get('access_token');
		const { itemId: fileId } = form.data;
		const { data, error } = await storageMoveToTrashFileFileIdPatch({
			headers: {
				Authorization: `Bearer ${token}`
			},
			path: {
				file_id: fileId
			}
		});

		return handleFormResponse(form, data, error);
	}
};
