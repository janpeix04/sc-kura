import { loginSchema } from '$lib/schemas/auth';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { fail, message, superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { loginPost, usersMeGet } from '$lib/client';
import { m } from '$lib/paraglide/messages';
import { localizeHref } from '$lib/paraglide/runtime';

export const load: PageServerLoad = async () => {
	const form = superValidate(zod4(loginSchema));
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
				path: '/',
				httpOnly: true,
				sameSite: 'strict',
				secure: true,
				maxAge: 18000
			});

			const { data: user, response } = await usersMeGet({
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});

			if (response.ok && user) {
				redirect(307, localizeHref('/storage'));
			}
		}

		if (error === undefined) return;

		if ('msg' in error) {
			return message(form, `${error.msg}`, { status: 400 });
		}

		return message(form, m.oops_something_went_wrong(), { status: 500 });
	}
};
