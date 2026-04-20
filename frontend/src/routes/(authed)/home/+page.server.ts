import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema } from '$lib/schemas/storage';
import type { Actions } from '@sveltejs/kit';
import {
	storageAvailableSpaceGet,
	storageFolderIdPost,
	storageFolderRootGet,
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
		createFolderForm: await superValidate(zod4(createFolderSchema))
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
	}
};
