<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { signupSchema, type SignupSchema } from '$lib/schemas/auth';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';

	let { data }: { data: { form: SuperValidated<SignupSchema> } } = $props();

	const form = superForm(data.form, {
		validators: zod4Client(signupSchema)
	});

	const { form: formData, enhance } = form;
</script>

<div class="flex min-h-screen items-center justify-center bg-gray-50 px-4">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-lg">
		<div class="text-center">
			<h1 class="text-2xl font-semibold tracking-tight">
				{m.signup()}
			</h1>
		</div>

		<form action="?/signup" method="POST" class="space-y-4" use:enhance>
			<Form.Field {form} name="firstName">
				<Form.Control>
					{#snippet children({ props })}
						<Form.Label class="text-sm font-medium">
							{m.first_name()}
						</Form.Label>
						<Input
							{...props}
							type="text"
							placeholder={m.first_name_placeholder()}
							autocomplete="username"
							bind:value={$formData.firstName}
						/>
					{/snippet}
				</Form.Control>
				<Form.FieldErrors />
			</Form.Field>
			<Form.Field {form} name="lastName">
				<Form.Control>
					{#snippet children({ props })}
						<Form.Label class="text-sm font-medium">
							{m.last_name()}
						</Form.Label>
						<Input
							{...props}
							type="text"
							autocomplete="username"
							placeholder={m.last_name_placeholder()}
							bind:value={$formData.lastName}
						/>
					{/snippet}
				</Form.Control>
				<Form.FieldErrors />
			</Form.Field>
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
			<Form.Field {form} name="confirmPassword">
				<Form.Control>
					{#snippet children({ props })}
						<Form.Label class="text-sm font-medium">
							{m.confirm_password()}
						</Form.Label>
						<Input
							{...props}
							type="password"
							placeholder="••••••••"
							autocomplete="new-password"
							bind:value={$formData.confirmPassword}
						/>
					{/snippet}
				</Form.Control>
				<Form.FieldErrors />
			</Form.Field>

			<Form.Button type="submit" class="w-full">
				{m.signup()}
			</Form.Button>
		</form>

		<div class="text-center text-xs text-muted-foreground">
			{m.have_an_account()} <a
				href={localizeHref('/login')}
				class="hover:underline hover:underline-offset-2">{m.login()}</a
			>
		</div>
	</div>
</div>
