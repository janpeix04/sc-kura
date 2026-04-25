import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from '../$types';

export const load: LayoutServerLoad = async ({ cookies }) => {
	const vaultSession = cookies.get('vault_session');

	if (!vaultSession) {
		throw redirect(307, '/personal-vault?login=true');
	}
};
