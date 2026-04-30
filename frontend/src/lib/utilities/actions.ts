import type { HttpMessage, HttpValidationError, UserPublic } from '$lib/client';
import { m } from '$lib/paraglide/messages';
import type { VerifyPasswordSchema } from '$lib/schemas/auth';
import type { CreateFolderSchema, MoveToTrashItemSchema } from '$lib/schemas/storage';
import type { UpdateUserSchema } from '$lib/schemas/user';
import type { ActionResult } from '@sveltejs/kit';
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
	form: SuperValidated<
		CreateFolderSchema | MoveToTrashItemSchema | UpdateUserSchema | VerifyPasswordSchema
	>,
	data: string | UserPublic | boolean | undefined,
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
