<script lang="ts">
	import * as Form from '$lib/components/ui/form/index';
	import { Input } from '$lib/components/ui/input/index';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { forgotPasswordSchema, type ForgotPasswordSchema } from '$lib/schemas/auth';
	import { toast } from 'svelte-sonner';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';

	let { data }: { data: { form: SuperValidated<ForgotPasswordSchema> } } = $props();

	const form = superForm(data.form, {
		validators: zod4Client(forgotPasswordSchema)
	});

	const { form: formData, enhance } = form;
</script>

<div class="flex min-h-screen items-center justify-center bg-gray-50 px-4">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-lg">
		<div class="space-y-2 text-center">
			<h1 class="text-2xl font-semibold tracking-tight">
				{m.forgot_password()}
			</h1>
			<p class="text-sm text-muted-foreground">
                {m.forgot_password_subtitle()}
            </p>
		</div>
		<form
			action="?/forgotPassword"
			method="POST"
			class="space-y-4"
			use:enhance={{
				onResult({ result }) {
					if (result.type === 'failure') {
						const form = result.data?.form;

						if (form.message) {
							toast.error(form.message, { duration: 5000 });
						}
					} else if (result.type === 'success') {
						const form = result.data?.form;

						if (form.message) {
							toast.info(form.message, { duration: 5000 });
						}
					}
				}
			}}
		>
			<Form.Field {form} name="email">
				<Form.Control>
					{#snippet children({ props })}
						<Form.Label class="text-sm font-medium">
							{m.email()}
						</Form.Label>
						<Input
							{...props}
							type="email"
							placeholder={m.email_placeholder()}
							autocomplete="email"
							bind:value={$formData.email}
							required
						/>
					{/snippet}
				</Form.Control>
				<Form.FieldErrors />
			</Form.Field>

			<Form.Button type="submit" class="w-full">
				{m.send_reset_link()}
			</Form.Button>
		</form>

		<div class="text-center text-xs text-muted-foreground">
			<a href={localizeHref('/login')} class="hover:underline hover:underline-offset-2">
				{m.login()}
			</a>
		</div>
	</div>
</div>
