import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { fail, message, setError, superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { signupSchema } from '$lib/schemas/auth';
import { signupPost } from '$lib/client';
import { getLocale, localizeHref } from '$lib/paraglide/runtime';
import { ORIGINS } from '$lib/schemas/types';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async () => {
	return {
		form: await superValidate(zod4(signupSchema))
	};
};

export const actions: Actions = {
	signup: async ({ request }) => {
		const form = await superValidate(request, zod4(signupSchema));

		if (!form.valid) {
			return fail(400, { form });
		}
		const { firstName, lastName, email, password } = form.data;
		const { data, error } = await signupPost({
			body: {
				first_name: firstName,
				last_name: lastName,
				email,
				password
			},
			query: {
				locale: getLocale()
			}
		});

		if (!error) {
			return redirect(303, localizeHref(`/login?message=${data}&origin=${ORIGINS.Signup}`));
		}

		if ('msg' in error) {
			if (error.loc === 'email') {
				return setError(form, 'email', `${error.msg}`);
			}
			return message(form, error.msg, { status: 400 });
		}
		return message(form, m.oops_something_went_wrong(), { status: 500 });
	}
};
