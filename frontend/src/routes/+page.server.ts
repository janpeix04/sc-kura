import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { localizeHref } from '$lib/paraglide/runtime';

export const load: PageServerLoad = () => {
	redirect(307, localizeHref('/login'));
};
