import {
	storageAvailableSpaceGet,
	storageFilesFolderIdGet,
	storageFolderIdPost,
	storageFolderRootGet,
	storageFoldersFolderIdGet,
	storageFolderVaultGet
} from '$lib/client';
import { superValidate, fail } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema } from '$lib/schemas/storage';
import type { Actions } from '@sveltejs/kit';
import { handleFormResponse } from '$lib/utilities/actions';

export const load: PageServerLoad = async ({ cookies }) => {
	const token = cookies.get('access_token');

	const { data: vault } = await storageFolderVaultGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		throwOnError: true
	});

	const availableSpacePromise = storageAvailableSpaceGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		throwOnError: true
	});

	const foldersPromise = storageFoldersFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: vault.id
		}
	});

	const filesPromise = storageFilesFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: vault.id
		}
	});

	const [{ data: availableSpace }, { data: folders }, { data: files }] = await Promise.all([
		availableSpacePromise,
		foldersPromise,
		filesPromise
	]);

	return {
		availableSpace,
		folders,
		files,
		createFolderForm: await superValidate(zod4(createFolderSchema))
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
	}
};
