import { fail, message, superValidate } from "sveltekit-superforms";
import type { PageServerLoad } from "../../../$types";
import { zod4 } from "sveltekit-superforms/adapters";
import { resetPasswordSchema } from "$lib/schemas/auth";
import { expiredTokenGet, resetPasswordTokenPost } from "$lib/client/sdk.gen";
import { redirect, type Actions } from "@sveltejs/kit";
import { ORIGINS } from "$lib/schemas/types";

export const load: PageServerLoad = async ({ params, cookies }) => {
    const form = await superValidate(zod4(resetPasswordSchema));
    const { data: isTokenUsed, error } = await expiredTokenGet({
        path: {
            token: params.token
        }
    });
    if (!error && !isTokenUsed) {
        cookies.set('reset_token', params.token, {
            path: '/',
            httpOnly: true,
            sameSite: 'strict',
            secure: true,
            maxAge: 60 * 60
        });
        return { form, success: true};
    }
    return { form, success: false, expired: true, message: 'Link has expired'}
}

export const actions: Actions = {
    resetPassowrd: async ({ request, cookies}) => {
        const form = await superValidate(request, zod4(resetPasswordSchema));
        const resetToken = cookies.get('reset_token');
        if (!resetToken) {
            return { form, success: false, expired: true, message: 'Link has expired'};
        }
        if (!form.valid) {
            return fail(400, { form});
        }

        const { data, error} = await resetPasswordTokenPost({
            path: { token: resetToken},
            body: { new_password: form.data.password}
        });

        if (!error) {
            return redirect(303, `/login?message=${data}&origin=${ORIGINS.ResetPassword}`);
        }
        if ('msg' in error) {
            return { form, success: false, expired: false, message: error.msg};
        }
        return { form, success: false, expired: false, message: 'Oops... Something went wrong!'};
    }
}