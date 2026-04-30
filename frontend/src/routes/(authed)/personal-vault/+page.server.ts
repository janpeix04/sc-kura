import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { verifyPasswordSchema } from '$lib/schemas/auth';
import { updateUserSchema } from '$lib/schemas/user';
import {
	cryptoRootGet,
	storageAvailableSpaceGet,
	usersMePatch,
	verifyPasswordPost
} from '$lib/client';
import { createFolderSchema } from '$lib/schemas/storage';
import type { Actions } from '@sveltejs/kit';
import { handleFormResponse } from '$lib/utilities/actions';

export const load: PageServerLoad = async ({ cookies, locals }) => {
	const token = cookies.get('access_token');

	const vaultPromise = cryptoRootGet({
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

	const [{ data: vault }, { data: availableSpace }] = await Promise.all([
		vaultPromise,
		availableSpacePromise
	]);

	return {
		availableSpace,
		folderId: vault.id,
		hasSeen: locals.user?.has_seen_personal_vault,
		createFolderForm: await superValidate(zod4(createFolderSchema)),
		verifyPasswordForm: await superValidate(zod4(verifyPasswordSchema)),
		updateUserForm: await superValidate(zod4(updateUserSchema))
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
				password
			}
		});

		return handleFormResponse(form, data, error);
	}
};
