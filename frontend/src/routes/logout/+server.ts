import { redirect, type RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ cookies }) => {
	cookies.delete('access_token', { path: '/' });
	cookies.delete('vault_session', { path: '/' });
	throw redirect(302, '/');
};
