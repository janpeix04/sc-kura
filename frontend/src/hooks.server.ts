import { loginRefreshTokenPost, usersMeGet } from '$lib/client';
import type { Cookies, Handle, RequestEvent } from '@sveltejs/kit';

export async function setTokenCookies(
	cookies: Cookies,
	access_token: string,
	refresh_token: string
) {
	cookies.set('access_token', access_token, {
		path: '/',
		httpOnly: true,
		sameSite: 'strict',
		secure: true,
		maxAge: 18000
	});
	cookies.set('refresh_token', refresh_token, {
		path: '/',
		httpOnly: true,
		sameSite: 'strict',
		secure: true,
		maxAge: 25200
	});
}

async function handleToken(cookies: Cookies) {
	const accessToken = cookies.get('access_token');
	const refreshToken = cookies.get('refresh_token');

	const fetchUserWithToken = async (token: string) => {
		const { data, response } = await usersMeGet({
			headers: {
				Authorization: `Bearer ${token}`
			}
		});
		return {
			user: data ?? null,
			status: response.status
		};
	};

	if (!accessToken) return null;

	const result = await fetchUserWithToken(accessToken);

	if (result.status === 200 && result.user) return result.user;
	if (refreshToken === undefined) return null;
	if (result.status !== 403) return null;

	const { data, response } = await loginRefreshTokenPost({
		query: {
			refresh_token: refreshToken
		}
	});

	if (!response.ok || !data) {
		cookies.delete('access_token', { path: '/' });
		cookies.delete('refresh_token', { path: '/' });
		return null;
	}
	setTokenCookies(cookies, data.access_token, data.refresh_token);
	const refreshed = await fetchUserWithToken(data.access_token);
	return refreshed.user;
}

function getBearerToken(event: RequestEvent): string | null {
	const auth = event.request.headers.get('authorization');
	if (auth?.toLowerCase().startsWith('bearer ')) return auth.slice(7).trim();
	const cookieToken = event.cookies.get('access_token');
	return cookieToken ?? null;
}

async function apiProxy(event: RequestEvent) {
	const { request, url } = event;
	const method = request.method;

	const token = getBearerToken(event);
	if (!token) return new Response('Unauthorized', { status: 401 });

	const apiURL = `http://localhost:8000${url.pathname}${url.search}`;

	const headers = new Headers();
	headers.set('authorization', `Bearer ${token}`);

	const contentType = request.headers.get('content-type');
	if (contentType) {
		headers.set('content-type', contentType);
	}

	const accept = request.headers.get('accept');
	if (accept) {
		headers.set('accept', accept);
	}

	const body = method === 'GET' || method === 'HEAD' ? undefined : request.body;

	return fetch(apiURL, { method, headers, body });
}

export const handle: Handle = async ({ event, resolve }) => {
	const { url, cookies } = event;

	event.locals.user = await handleToken(cookies);

	if (url.pathname.startsWith('/api')) {
		return apiProxy(event);
	}
	return resolve(event);
};
