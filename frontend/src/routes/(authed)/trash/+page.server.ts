import {
	storageFolderIdPost,
	storageFoldersFolderIdGet,
	type FolderPublic,
	storageFilesFolderIdGet,
	storageFolderRootGet,
	storageAvailableSpaceGet
} from '$lib/client';
import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema } from '$lib/schemas/storage';
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
		},
		query: {
			status: 'deleted'
		}
	});

	const filesPromise = storageFilesFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: root.id
		},
		query: {
			status: 'deleted'
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
