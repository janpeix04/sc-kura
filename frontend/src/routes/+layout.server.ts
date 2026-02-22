import { storageAvailableSpaceGet, type UserPublic } from '$lib/client';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, cookies }) => {
	const token = cookies.get('access_token');
	const { data: availableSpace } = await storageAvailableSpaceGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	})
	return {
		user: locals.user as UserPublic, 
		availableSpace
	};
};
