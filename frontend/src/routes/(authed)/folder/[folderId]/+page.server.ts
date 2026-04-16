import {
	storageAvailableSpaceGet,
	storageBreadcrumbsFolderIdGet,
	storageFilesFolderIdGet,
	storageFolderIdPost,
	storageFoldersFolderIdGet,
	storageMoveToTrashFileFileIdPatch,
	storageRenameFileFileIdPatch,
	storageRenameFolderFolderIdPatch
} from '$lib/client';
import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema, moveToTrashItemSchema, renameItemSchema } from '$lib/schemas/storage';
import type { Actions } from '@sveltejs/kit';
import { handleFormResponse } from '$lib/utilities/actions';

export const load: PageServerLoad = async ({ cookies, params, depends }) => {
	depends('data:folder');

	const folderId = params.folderId;
	const token = cookies.get('access_token');

	const breadcrumbsPromise = storageBreadcrumbsFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: folderId
		}
	});

	const foldersPromise = storageFoldersFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: folderId
		}
	});

	const filesPromise = storageFilesFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: folderId
		}
	});

	const availableSpacePromise = storageAvailableSpaceGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const [{ data: breadcrumbs }, { data: folders }, { data: files }, { data: availableSpace }] =
		await Promise.all([breadcrumbsPromise, foldersPromise, filesPromise, availableSpacePromise]);

	return {
		breadcrumbs,
		folders,
		files,
		folderId,
		availableSpace,
		createFolderForm: await superValidate(zod4(createFolderSchema)),
		renameItemForm: await superValidate(zod4(renameItemSchema)),
		moveToTrashItemForm: await superValidate(zod4(moveToTrashItemSchema))
	};
};

export const actions: Actions = {
	createFolder: async ({ request, params, cookies }) => {
		const form = await superValidate(request, zod4(createFolderSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const token = cookies.get('access_token');
		const folderId = params.folderId as string;

		const { name } = form.data;
		const { data, error } = await storageFolderIdPost({
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
