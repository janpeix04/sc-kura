import { fail, setError, superValidate } from "sveltekit-superforms";
import type { PageServerLoad } from "../../$types";
import { zod4 } from "sveltekit-superforms/adapters";
import { forgotPasswordSchema } from "$lib/schemas/auth";
import type { Actions } from "@sveltejs/kit";
import { forgotPasswordPost } from "$lib/client/sdk.gen";

export const load: PageServerLoad = async () => {
    return {
        form: superValidate(zod4(forgotPasswordSchema))
    }
}

export const actions: Actions = {
    forgotPassword: async ({request}) => {
        const form = await superValidate(request, zod4(forgotPasswordSchema));

        if (!form.data) {
            return fail(400, { form });
        }

        const { data, error } = await forgotPasswordPost({
            body: {
                email: form.data.email
            }
        });

        if (!error) {
            return { form, success: true, message: data};
        }

        if ('msg' in error) {
            if (error.loc === 'email') {
                return setError(form, 'email', error.msg);
            }
            return {form, success: false, message: error.msg};
        }
        return { form, success: false, message: 'Oops... Something went wrong!'};
    }
}