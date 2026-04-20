import {
	storageAvailableSpaceGet,
	storageBreadcrumbsFolderIdGet,
	storageFilesFolderIdGet,
	storageFolderIdPost,
	storageFoldersFolderIdGet
} from '$lib/client';
import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema } from '$lib/schemas/storage';
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
		createFolderForm: await superValidate(zod4(createFolderSchema))
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
	}
};
