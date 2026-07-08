import { signupPost } from '$lib/client';
import { m } from '$lib/paraglide/messages';
import { getLocale, localizeHref } from '$lib/paraglide/runtime';
import { ORIGINS } from '$lib/schemas/types';
import { redirect, type Actions } from '@sveltejs/kit';

export const actions: Actions = {
	signup: async ({ request }) => {
		const form = await request.formData();

		const firstName = form.get('firstName') as string;
		const lastName = form.get('lastName') as string | null | undefined;
		const email = form.get('email') as string;
		const password = form.get('password') as string;

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
			return { success: false, message: error.msg, loc: error.loc };
		}

		return { success: false, message: m.oops_something_went_wrong() };
	}
};
