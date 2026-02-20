import { redirect, type RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ cookies }) => {
	cookies.delete('access_token', { path: '/' });
	throw redirect(302, '/');
};
