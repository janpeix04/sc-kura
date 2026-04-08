import type { HttpMessage, HttpValidationError } from '$lib/client';
import { m } from '$lib/paraglide/messages';
import type { CreateFolderSchema } from '$lib/schemas/storage';
import type { ActionResult, HttpError } from '@sveltejs/kit';
import { toast } from 'svelte-sonner';
import { message, type SuperValidated } from 'sveltekit-superforms';

export function superFormOnResult({
	result
}: {
	result: ActionResult;
	formEl: HTMLFormElement;
	formElement: HTMLFormElement;
	cancel: () => void;
}) {
	if (result.type === 'failure') {
		const form = result.data?.form;

		if (form.message) {
			toast.error(form.message);
		}
	}
	if (result.type === 'success') {
		const form = result.data?.form;

		if (form.message) {
			toast.success(form.message);
		}
	}
}

export function handleFormResponse(
	form: SuperValidated<CreateFolderSchema>,
	data: string | undefined,
	error: HttpValidationError | HttpMessage | undefined
) {
	if (!error) {
		return message(form, data);
	}

	if ('msg' in error) {
		return message(form, error.msg, { status: 400 });
	}
	return message(form, m.oops_something_went_wrong(), { status: 500 });
}
