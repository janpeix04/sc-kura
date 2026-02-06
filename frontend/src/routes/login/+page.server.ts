import { fail, message, superValidate } from "sveltekit-superforms";
import type { PageServerLoad } from "../$types";
import { zod4 } from "sveltekit-superforms/adapters";
import { loginSchema } from "$lib/schemas/auth";
import { redirect, type Actions } from "@sveltejs/kit";
import { loginPost, usersMeGet } from "$lib/client";
import { setTokenCookies } from "../../hooks.server";

export const load: PageServerLoad = async ({url}) => {
    const origin = url.searchParams.get('origin');
    const message = url.searchParams.get('message');
    
    const form = superValidate(zod4(loginSchema));

    if (origin && message) {
        return {
            form,
            origin,
            message
        }
    }
    return {
        form
    }
}

export const actions: Actions = {
    login: async ({ request, cookies }) => {
        const form = await superValidate(request, zod4(loginSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        const { username, password } = form.data;
        const {data, error} = await loginPost({
            body: {
                username,
                password
            }
        });

        if (!error) {
            const { access_token, refresh_token} = data;
            setTokenCookies(cookies, access_token, refresh_token);
            
            const {data: user, response} = await usersMeGet({
                headers: {
                    Authorization: `Bearer ${access_token}`
                }
            });

            if (response.ok && user) {
                redirect(303, '/storage');
            }
        }
        if (error === undefined) return;

        if ('msg' in error) {
            return message(form, `${error.msg}`, { status: 400 });
        }
    }
}