import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { loginPost, usersMeGet } from '$lib/client';
import { localizeHref } from '$lib/paraglide/runtime';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ url }) => {
	const origin = url.searchParams.get('origin');
	const message = url.searchParams.get('message');

	if (origin && message) {
		return {
			origin,
			message
		};
	}
};

export const actions: Actions = {
	login: async ({ request, cookies }) => {
		const form = await request.formData();

		const username = form.get('email') as string;
		const password = form.get('password') as string;

		const { data, error } = await loginPost({
			body: {
				username,
				password
			}
		});

		if (!error) {
			const { access_token } = data;
			cookies.set('access_token', access_token, {
				httpOnly: true,
				secure: true,
				sameSite: 'lax',
				path: '/',
				maxAge: 60 * 60
			});

			const { data: user, response } = await usersMeGet({
				headers: { Authorization: `Bearer ${access_token}` }
			});

			if (response.ok && user) {
				return redirect(303, localizeHref('/home'));
			}
		}

		if (error && 'msg' in error) {
			return { success: false, message: error.msg, loc: error.loc };
		}

		return { success: false, message: m.oops_something_went_wrong() };
	}
};
