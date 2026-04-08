import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema, renameItemSchema } from '$lib/schemas/storage';
import type { Actions } from '@sveltejs/kit';
import {
	storageFolderFolderIdPatch,
	storageFolderIdPost,
	storageFolderRootGet,
	storageSuggestedFoldersGet
} from '$lib/client';
import { handleFormResponse } from '$lib/utilities/actions';

export const load: PageServerLoad = async ({ cookies }) => {
	const token = cookies.get('access_token');

	const suggestedFoldersPromise = storageSuggestedFoldersGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const [{ data: suggestedFolders }] = await Promise.all([suggestedFoldersPromise]);

	return {
		createFolderForm: await superValidate(zod4(createFolderSchema)),
		renameItemForm: await superValidate(zod4(renameItemSchema)),
		suggestedFolders
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
		const { data, error } = await storageFolderFolderIdPatch({
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
	}
};
