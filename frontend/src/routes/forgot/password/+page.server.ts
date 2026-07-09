import type { Actions } from '@sveltejs/kit';
import { forgotPasswordPost } from '$lib/client';
import { m } from '$lib/paraglide/messages';
import { getLocale } from '$lib/paraglide/runtime';

export const actions: Actions = {
	forgotPassword: async ({ request }) => {
		const form = await request.formData();
		const email = form.get('email') as string;

		const { data, error } = await forgotPasswordPost({
			body: {
				email
			},
			query: {
				locale: getLocale()
			}
		});

		if (!error) {
			return { success: true, message: data };
		}

		if ('msg' in error) {
			return { success: false, message: error.msg };
		}
		return { success: false, message: m.oops_something_went_wrong() };
	}
};
