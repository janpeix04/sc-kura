import type { PageServerLoad } from './$types';
import { expiredTokenGet, resetPasswordTokenPost } from '$lib/client';
import { m } from '$lib/paraglide/messages';
import { redirect, type Actions } from '@sveltejs/kit';
import { localizeHref } from '$lib/paraglide/runtime';
import { ORIGINS } from '$lib/schemas/types';

export const load: PageServerLoad = async ({ params, cookies }) => {
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

		return { success: true };
	}

	return {
		success: false,
		expired: true,
		message: m.link_has_expired()
	};
};

export const actions: Actions = {
	resetPassword: async ({ request, cookies }) => {
		const form = await request.formData();
		const password = form.get('password') as string;

		const resetToken = cookies.get('reset_token');

		if (resetToken === undefined) {
			return { success: false, message: m.link_has_expired() };
		}

		const { data, error } = await resetPasswordTokenPost({
			path: {
				token: resetToken
			},
			body: {
				new_password: password
			}
		});

		if (!error) {
			return redirect(
				303,
				localizeHref(`/login?message=${encodeURIComponent(data)}&origin=${ORIGINS.ResetPassword}`)
			);
		}

		if ('msg' in error) {
			return { success: false, message: error.msg };
		}
		return { success: false, message: m.oops_something_went_wrong() };
	}
};
