import type { Handle, RequestEvent } from '@sveltejs/kit';
import { paraglideMiddleware } from '$lib/paraglide/server';
import { getTextDirection } from '$lib/paraglide/runtime';
import { usersMeGet } from '$lib/client';

function getBearerToken(event: RequestEvent): string | null {
	const auth = event.request.headers.get('authorization');
	if (auth?.toLowerCase().startsWith('bearer ')) return auth.slice(7).trim();

	const cookieToken = event.cookies.get('access_token');
	return cookieToken ?? null;
}

async function apiProxy(event: RequestEvent) {
	const { request, url, cookies } = event;
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

	const locale = cookies.get('PARAGLIDE_LOCALE');
	if (locale) headers.set('x-locale', locale);

	const body = method === 'GET' || method === 'HEAD' ? undefined : request.body;

	return fetch(apiURL, { method, headers, body });
}

export const handle: Handle = async ({ event, resolve }) => {
	const { url, cookies } = event;
	const token = cookies.get('access_token');

	if (token) {
		const { data, response } = await usersMeGet({
			headers: {
				Authorization: `Bearer ${token}`
			}
		});
		if (response.ok && data) {
			event.locals.user = data;
		}
	}

	if (url.pathname.startsWith('/api/v1/')) {
		return apiProxy(event);
	}

	return paraglideMiddleware(event.request, ({ request: localizedRequest, locale }) => {
		event.request = localizedRequest;
		return resolve(event, {
			transformPageChunk: ({ html }) => {
				return html.replace('%lang%', locale).replace('%dir%', getTextDirection(locale));
			}
		});
	});
};
