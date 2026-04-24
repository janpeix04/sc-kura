import {
	storageAvailableSpaceGet,
	storageFilesFolderIdGet,
	storageFolderIdPost,
	storageFolderRootGet,
	storageFoldersFolderIdGet,
	storageFolderVaultGet,
	usersMePatch
} from '$lib/client';
import { superValidate, fail, message } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema } from '$lib/schemas/storage';
import type { Actions } from '@sveltejs/kit';
import { handleFormResponse } from '$lib/utilities/actions';
import { updateUserSchema } from '$lib/schemas/user';
import { m } from '$lib/paraglide/messages';

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
		createFolderForm: await superValidate(zod4(createFolderSchema)),
		updateUserForm: await superValidate(zod4(updateUserSchema))
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
	markHasSeenPersonalVault: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(updateUserSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const token = cookies.get('access_token');
		const { hasSeenPersonalVault } = form.data;
		const { error } = await usersMePatch({
			headers: {
				Authorization: `Bearer ${token}`
			},
			body: {
				has_seen_personal_vault: hasSeenPersonalVault
			}
		});

		if (error === undefined) return;

		if ('msg' in error) {
			return message(form, error.msg, { status: 400 });
		}
		return message(form, m.oops_something_went_wrong(), { status: 500 });
	}
};
