import type { PageServerLoad } from './$types';
import { fail, message, setError, superValidate } from 'sveltekit-superforms';
import { signupSchema } from '$lib/schemas/auth';
import { zod4 } from 'sveltekit-superforms/adapters';
import { redirect, type Actions } from '@sveltejs/kit';
import { usersSignupPost } from '$lib/client';
import { ORIGINS } from '$lib/schemas/types';

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
		const { username, email, password } = form.data;
		const { data, error } = await usersSignupPost({
			body: {
				username,
				email,
				password
			}
		});
		if (!error) {
			return redirect(303, `/login?message=${data}&origin=${ORIGINS.Signup}`);
		}

		if ('msg' in error) {
			if (error.loc === 'email') return setError(form, 'email', `${error.msg}`);
			if ('msg' in error) {
				if (error.loc === 'email') return setError(form, 'email', `${error.msg}`);

				return message(form, error.msg, { status: 400 });
			}
			return message(form, 'Oops... Something went wrong!', { status: 500 });
		}
	}
};
