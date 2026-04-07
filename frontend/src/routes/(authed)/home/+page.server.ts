import { fail, superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { createFolderSchema } from '$lib/schemas/storage';
import type { Actions } from '@sveltejs/kit';

export const load: PageServerLoad = async () => {
	return {
		createFolderForm: await superValidate(zod4(createFolderSchema))
	};
};

export const actions: Actions = {
	createFolder: async ({ request }) => {
		const form = await superValidate(request, zod4(createFolderSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

        console.log(form)
	}
};
