import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { resetPasswordSchema, verifyPasswordSchema } from '$lib/schemas/auth';
import { updateUserSchema } from '$lib/schemas/user';
import {
	cryptoFilesFolderIdGet,
	cryptoFoldersFolderIdGet,
	cryptoRootGet,
	storageAvailableSpaceGet,
	usersMePatch,
	verifyPasswordPost
} from '$lib/client';
import type { Actions } from '@sveltejs/kit';
import { handleFormResponse } from '$lib/utilities/actions';

export const load: PageServerLoad = async ({ cookies, depends, locals }) => {
	depends('data:personal-vault');
	const token = cookies.get('access_token');

	const { data: vault } = await cryptoRootGet({
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

	const foldersPromise = cryptoFoldersFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: vault.id
		}
	});

	const filesPromise = cryptoFilesFolderIdGet({
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
		folderId: vault.id,
		files,
		hasSeen: locals.user?.has_seen_personal_vault,
		verifyPasswordForm: await superValidate(zod4(verifyPasswordSchema)),
		updateUserForm: await superValidate(zod4(updateUserSchema)),
		resetPasswordForm: await superValidate(zod4(resetPasswordSchema))
	};
};

export const actions: Actions = {
	markHasSeenPersonalVault: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(updateUserSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const token = cookies.get('access_token');
		const { hasSeenPersonalVault } = form.data;
		const { data, error } = await usersMePatch({
			headers: {
				Authorization: `Bearer ${token}`
			},
			body: {
				has_seen_personal_vault: hasSeenPersonalVault
			}
		});
		return handleFormResponse(form, data, error);
	},
	verifyPassword: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(verifyPasswordSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const token = cookies.get('access_token');
		const { password } = form.data;

		const { data, error } = await verifyPasswordPost({
			headers: {
				Authorization: `Bearer ${token}`
			},
			query: {
				password,
				isVault: true
			}
		});

		return handleFormResponse(form, data, error);
	}
};
