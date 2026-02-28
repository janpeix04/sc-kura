<script lang="ts">
	import * as Form from '$lib/components/ui/form/index';
	import { Input } from '$lib/components/ui/input/index';
	import { type SuperValidated, type Infer, superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { toast } from 'svelte-sonner';
	import { resetPasswordSchema, type ResetPasswordSchema } from '$lib/schemas/auth';

	let { data }: { data: { form: SuperValidated<Infer<ResetPasswordSchema>> } } = $props();

	const form = superForm(data.form, {
		validators: zod4Client(resetPasswordSchema)
	});

	const { form: formData, enhance } = form;
</script>

<div class="bg-primary flex h-full w-full items-center justify-center">
	<form
		action="?/resetPassword"
		method="POST"
		class="bg-secondary w-105 rounded-3xl px-10 py-6"
		use:enhance={{
			async onResult({ result }) {
				if (result.type === 'success') {
					const form = result.data?.form;

					if (form.message) {
						toast.info(form.message, { duration: 8000 });
					}
				} else if (result.type === 'failure') {
					const form = result.data?.form;
					if (form.message) {
						toast.error(form.message);
					}
				}
			}
		}}
	>
		<div class="mb-8 text-center">
			<h2 class="text-xl font-semibold">Reset Password</h2>
		</div>

		<Form.Field {form} name="password">
			<Form.Control>
				{#snippet children({ props })}
					<Form.Label>Passowrd</Form.Label>
					<Input
						{...props}
						bind:value={$formData.password}
						type="password"
						autocomplete="new-password"
						placeholder="*******"
						required
					/>
				{/snippet}
			</Form.Control>
			<Form.FieldErrors />
		</Form.Field>
		<Form.Field {form} name="password-confirm">
			<Form.Control>
				{#snippet children({ props })}
					<Form.Label>Confirm Password</Form.Label>
					<Input
						{...props}
						bind:value={$formData['password-confirm']}
						type="password"
						autocomplete="current-password"
						placeholder="*******"
						required
					/>
				{/snippet}
			</Form.Control>
			<Form.FieldErrors />
		</Form.Field>
		<Form.Button class="mt-4 h-11 w-full cursor-pointer px-2.5" type="submit">Submit</Form.Button>
	</form>
</div>
