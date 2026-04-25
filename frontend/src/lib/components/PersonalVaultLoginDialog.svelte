<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Form from '$lib/components/ui/form';
	import { m } from '$lib/paraglide/messages';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import Button from './ui/button/button.svelte';
	import Input from './ui/input/input.svelte';
	import { verifyPasswordSchema, type VerifyPasswordSchema } from '$lib/schemas/auth';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { toast } from 'svelte-sonner';

	let {
		open = $bindable(),
		verifyPasswordForm
	}: {
		open: boolean;
		verifyPasswordForm: SuperValidated<VerifyPasswordSchema>;
	} = $props();

	const form = superForm(verifyPasswordForm, {
		validators: zod4Client(verifyPasswordSchema)
	});

	const { form: formData, enhance } = form;
</script>

<Dialog.Root bind:open>
	<Dialog.Content
		showCloseButton={false}
		onInteractOutside={(e) => e.preventDefault()}
		onEscapeKeydown={(e) => e.preventDefault()}
		class="sm:max-w-md"
	>
		<form
			action="?/verifyPassword"
			method="POST"
			class="flex flex-col gap-4"
			use:enhance={{
				onResult({ result }) {
					if (result.type === 'failure') {
						const form = result.data?.form;

						if (form.message) {
							toast.error(form.message);
						}
					}

					if (result.type === 'success') {
						const form = result.data?.form;

						const correct = form.message;

						if (correct) {
							open = false;
						} else {
							toast.error(m.incorrect_password());
						}
					}
				}
			}}
		>
			<div class="flex flex-col gap-1">
				<h2 class="text-lg font-semibold">{m.enter_your_passowrd()}</h2>
				<p class="text-sm text-muted-foreground">
					{m.enter_your_password_description()}
				</p>
			</div>

			<Form.Field {form} name="password">
				<Form.Control>
					{#snippet children({ props })}
						<Input
							{...props}
							type="password"
							placeholder="••••••••"
							autocomplete="current-password"
							bind:value={$formData.password}
							required
						/>
					{/snippet}
				</Form.Control>
				<Form.FieldErrors />
			</Form.Field>

			<div class="flex items-center justify-between">
				<a href="#" class="text-sm text-muted-foreground underline hover:text-foreground">
					{m.forgot_password()}
				</a>

				<Button type="submit">
					{m.continue()}
				</Button>
			</div>
		</form>
	</Dialog.Content>
</Dialog.Root>
