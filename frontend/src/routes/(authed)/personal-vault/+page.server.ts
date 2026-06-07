import { fail, message, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { resetVaultPasswordSchema, verifyPasswordSchema } from '$lib/schemas/auth';
import { updateUserSchema } from '$lib/schemas/user';
import {
	cryptoFilesFolderIdGet,
	cryptoFoldersFolderIdGet,
	cryptoRootGet,
	cryptoUserKeysPatch,
	storageAvailableSpaceGet,
	usersMePatch,
	verifyPasswordPost
} from '$lib/client';
import type { Actions } from '@sveltejs/kit';
import { handleFormResponse } from '$lib/utilities/actions';
import { m } from '$lib/paraglide/messages';

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
		resetPasswordForm: await superValidate(zod4(resetVaultPasswordSchema))
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
	},
	resetPassword: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(resetVaultPasswordSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const token = cookies.get('access_token');
		const { password, encryptedPrivateKey, iv, salt, encryptedPrivateKeyRecovery, iv_recovery } =
			form.data;

		const { data: res } = await usersMePatch({
			headers: {
				Authorization: `Bearer ${token}`
			},
			body: {
				vault_password: password
			},
			throwOnError: true
		});

		if (!res) {
			return message(form, m.oops_something_went_wrong(), { status: 500 });
		}

		const { data, error } = await cryptoUserKeysPatch({
			headers: {
				Authorization: `Bearer ${token}`
			},
			body: {
				encrypted_private_key: encryptedPrivateKey,
				iv,
				pbkdf2_salt: salt,
				encrypted_private_key_recovery: encryptedPrivateKeyRecovery,
				iv_recovery
			}
		});

		if (!error) {
			return message(form, data);
		}

		if ('msg' in error) {
			return message(form, error.msg, { status: 400 });
		}

		return message(form, m.oops_something_went_wrong(), { status: 500 });
	}
};
