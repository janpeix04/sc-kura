import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { fail, message, superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { loginSchema } from '$lib/schemas/auth';
import { loginPost, usersMeGet } from '$lib/client';
import { localizeHref } from '$lib/paraglide/runtime';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ url }) => {
	const origin = url.searchParams.get('origin');
	const message = url.searchParams.get('message');

	const form = await superValidate(zod4(loginSchema));

	if (origin && message) {
		return {
			form,
			origin,
			message
		};
	}
	return {
		form
	};
};

export const actions: Actions = {
	login: async ({ request, cookies }) => {
		const form = await superValidate(request, zod4(loginSchema));

		if (!form.valid) {
			return fail(400, { form });
		}
		const { username, password } = form.data;
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
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});

			if (response.ok && user) {
				redirect(303, localizeHref(`/home`));
			}
		}

		if (error === undefined) return message(form, m.oops_something_went_wrong(), { status: 500 });

		if ('msg' in error) {
			return message(form, error.msg, { status: 400 });
		}
		return message(form, m.oops_something_went_wrong(), { status: 500 });
	}
};
