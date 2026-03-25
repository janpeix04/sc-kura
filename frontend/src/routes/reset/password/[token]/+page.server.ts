import { fail, message, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { resetPasswordSchema } from '$lib/schemas/auth';
import { expiredTokenGet, resetPasswordTokenPost } from '$lib/client';
import { m } from '$lib/paraglide/messages';
import { redirect, type Actions } from '@sveltejs/kit';
import { localizeHref } from '$lib/paraglide/runtime';
import { ORIGINS } from '$lib/schemas/types';

export const load: PageServerLoad = async ({ params, cookies }) => {
	const form = await superValidate(zod4(resetPasswordSchema));
	const token = params.token;

	const { data: isTokenUsed, error } = await expiredTokenGet({
		path: {
			token
		}
	});

	if (!isTokenUsed && !error) {
		cookies.set('reset_token', token, {
			httpOnly: true,
			secure: true,
			sameSite: 'strict',
			path: '/',
			maxAge: 60 * 60
		});

		return { form, success: true };
	}

	return {
		form,
		success: false,
		expired: true,
		message: m.link_has_expired()
	};
};

export const actions: Actions = {
	resetPassword: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(resetPasswordSchema));
		const resetToken = cookies.get('reset_token');

		if (resetToken === undefined) {
			return message(form, m.link_has_expired(), { status: 400 });
		}

		if (!form.valid) {
			fail(400, { form });
		}

		const { password } = form.data;
		const { data, error } = await resetPasswordTokenPost({
			path: {
				token: resetToken
			},
			body: {
				new_password: password
			}
		});

		if (!error) {
			throw redirect(
				303,
				localizeHref(`/login?message=${encodeURIComponent(data)}&origin=${ORIGINS.ResetPassword}`)
			);
		}

		if ('msg' in error) {
			return message(form, error.msg, { status: 400 });
		}
		return message(form, m.oops_something_went_wrong(), { status: 500 });
	}
};
