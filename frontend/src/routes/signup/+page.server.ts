import { type Actions } from '@sveltejs/kit';

export const actions: Actions = {
	signup: async ({ request }) => {
		const form = await request.formData();

		console.log(form);

		/* const { data, error } = await signupPost({
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
		return message(form, m.oops_something_went_wrong(), { status: 500 }); */
	}
};
