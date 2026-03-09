import type { UserPublic } from '$lib/client';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, cookies }) => {
	return {
		user: locals.user as UserPublic, 
	};
};
