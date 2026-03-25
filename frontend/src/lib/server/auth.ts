import { getRequestEvent } from "$app/server";
import { localizeHref } from "$lib/paraglide/runtime";
import { redirect } from "@sveltejs/kit";

export function requireLogin() {
    const { locals, url } = getRequestEvent();
    if (!locals.user) {
        const redirectTo = url.pathname + url.search;
        const params = new URLSearchParams({ redirectTo });
        redirect(307, localizeHref(`/login?${params}`));
    }
    return locals.user;
}