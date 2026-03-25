import { fail, message, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from '../../login/$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { forgotPasswordSchema } from '$lib/schemas/auth';
import type { Actions } from '@sveltejs/kit';
import { forgotPasswordPost } from '$lib/client';
import { m } from '$lib/paraglide/messages';
import { getLocale } from '$lib/paraglide/runtime';

export const load: PageServerLoad = async () => {
	return {
		form: await superValidate(zod4(forgotPasswordSchema))
	};
};

export const actions: Actions = {
	forgotPassword: async ({ request }) => {
		const form = await superValidate(request, zod4(forgotPasswordSchema));

		if (!form.valid) {
			fail(400, { form });
		}

		const { email } = form.data;
		const { data, error } = await forgotPasswordPost({
			body: {
				email
			},
            query: {
                locale: getLocale()
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
