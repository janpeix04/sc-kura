import { verifyAccountTokenPut } from '$lib/client';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	const { data, error } = await verifyAccountTokenPut({
		path: {
			token: params.token
		}
	});

	if (!error) {
		return { success: data };
	}

	if ('msg' in error) {
		return { error: error.msg };
	}
	return { error: m.oops_something_went_wrong() };
};
