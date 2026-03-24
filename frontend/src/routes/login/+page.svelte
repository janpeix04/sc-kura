<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { loginSchema, type LoginSchema } from '$lib/schemas/auth';
	import { ORIGINS } from '$lib/schemas/types';
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';

	let {
		data
	}: {
		data: {
			form: SuperValidated<LoginSchema>;
			origin: ORIGINS;
			message: string;
		};
	} = $props();

	const form = superForm(data.form, {
		validators: zod4Client(loginSchema)
	});

	const { form: formData, enhance } = form;

	onMount(() => {
		if (data.origin === ORIGINS.Signup) {
			toast.info(data.message, {duration: 5000});
		}
	});
</script>

<div class="flex min-h-screen items-center justify-center bg-gray-50 px-4">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-lg">
		<div class="text-center">
			<h1 class="text-2xl font-semibold tracking-tight">
				{m.login()}
			</h1>
		</div>

		<form
			action="?/login"
			method="POST"
			class="space-y-4"
			use:enhance={{
				onResult({ result }) {
					if (result.type === 'failure') {
						const form = result.data?.form;

						if (form?.message) {
							toast.error(form.message, { duration: 5000 });
						}
					}
				}
			}}
		>
			<Form.Field {form} name="username">
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
							bind:value={$formData.username}
						/>
					{/snippet}
				</Form.Control>
				<Form.FieldErrors />
			</Form.Field>
			<Form.Field {form} name="password">
				<Form.Control>
					{#snippet children({ props })}
						<Form.Label class="text-sm font-medium">
							{m.password()}
						</Form.Label>
						<Input
							{...props}
							type="password"
							placeholder="••••••••"
							autocomplete="new-password"
							bind:value={$formData.password}
						/>
					{/snippet}
				</Form.Control>
				<Form.FieldErrors />
			</Form.Field>
			<div class="text-right text-xs text-muted-foreground">
				<a href={localizeHref('/forgot/password')}>{m.forgot_password()}</a>
			</div>

			<Form.Button type="submit" class="w-full">
				{m.login()}
			</Form.Button>
		</form>

		<div class="text-center text-xs text-muted-foreground">
			{m.dont_have_an_account()}
			<a href={localizeHref('/signup')} class="hover:underline hover:underline-offset-2"
				>{m.create_account()}</a
			>
		</div>
	</div>
</div>
