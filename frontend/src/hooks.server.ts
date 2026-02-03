import type { Handle, RequestEvent } from "@sveltejs/kit";


async function apiProxy(event: RequestEvent) {
    const { request, url } = event;
    const method = request.method;

    const apiURL = `http://localhost:8000${url.pathname}${url.search}`;

    const headers = new Headers();
    
    const contentType = request.headers.get('content-type');
    if (contentType) {
        headers.set('content-type', contentType);
    }

    const accept = request.headers.get('accept');
    if (accept) {
        headers.set('accept', accept);
    }

    const body = method === 'GET' || method === 'HEAD' ? undefined : request.body;

    return fetch(apiURL, { method, headers, body})
}

export const handle: Handle = async ({ event, resolve }) => {
    if (event.url.pathname.startsWith('/api')) {
        return apiProxy(event);
    }
    return await resolve(event);
}