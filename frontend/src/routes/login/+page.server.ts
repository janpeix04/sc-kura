import { loginSchema } from '$lib/schemas/auth';
import type { PageServerLoad } from './$types';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';

export const load: PageServerLoad = async () => {
	const form = superValidate(zod4(loginSchema));
    return {
        form
    }
};
