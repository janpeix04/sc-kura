<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { m } from '$lib/paraglide/messages';
	import { loginSchema, type LoginSchema } from '$lib/schemas/auth.js';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import type { Infer } from 'zod';

	let { data }: { data: { form: SuperValidated<Infer<LoginSchema>> } } = $props();

	const form = superForm(data.form, {
		validators: zod4Client(loginSchema)
	});

	const { form: formData } = form;
</script>

<div class="flex min-h-screen items-center justify-center bg-gray-50 px-4">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-lg">
		<div class="space-y-2 text-center">
			<h1 class="text-2xl font-semibold tracking-tight">
				{m.login()}
			</h1>
			<p class="text-sm text-muted-foreground">{m.login_subtitle()}</p>
		</div>

		<form action="?/login" method="POST" class="space-y-4">
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
							autocomplete="current-password"
							bind:value={$formData.password}
						/>
					{/snippet}
				</Form.Control>
				<Form.FieldErrors />
			</Form.Field>
			
			<div class="text-right text-xs text-muted-foreground">
				{m.forgot_password()}
			</div>

			<Form.Button type="submit" class="w-full">
				{m.login()}
			</Form.Button>
		</form>

		<div class="text-center text-xs text-muted-foreground">
			{m.dont_have_an_account()}
			{m.create_account()}
		</div>
	</div>
</div>
