<script lang="ts">
	import { enhance } from '$app/forms';
	import Button from '$lib/components/ui/button/button.svelte';
	import { Input } from '$lib/components/ui/input';
	import Label from '$lib/components/ui/label/label.svelte';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { checkPasswordStrength } from '$lib/utilities/password-strength';

	let firstName: string = $state('');
	let lastName: string = $state('');
	let email: string = $state('');
	let password: string = $state('');

	let errors: Record<string, string | undefined> = $state({});
</script>

<div class="flex min-h-screen items-center justify-center bg-background">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-md">
		<div class="flex flex-col justify-center">
			<h1 class="text-lg font-bold">{m.create_new_free_account({ appName: 'Kura' })}</h1>

			<div class="flex items-center gap-2 text-sm text-muted-foreground">
				<span>{m.have_an_account()}</span>
				<a href={localizeHref('/login')} class="hover:underline hover:underline-offset-2"
					>{m.login()}</a
				>
			</div>
		</div>

		<form action="?/signup" method="POST" class="space-y-6" use:enhance>
			<div class="flex items-center gap-2">
				<div class="flex flex-1 flex-col gap-2">
					<Label for="firstName">
						{m.first_name()}
						<span class="text-destructive">*</span>
					</Label>
					<Input
						type="text"
						id="firstName"
						name="firstName"
						autocomplete="username"
						bind:value={firstName}
					/>
				</div>

				<div class="flex flex-1 flex-col gap-2">
					<Label for="lastName">
						{m.last_name()}
						<span class="text-muted-foreground">(optional)</span>
					</Label>
					<Input
						type="text"
						id="lastName"
						name="lastName"
						autocomplete="username"
						bind:value={lastName}
					/>
				</div>
			</div>

			<div class="flex flex-1 flex-col gap-2">
				<Label for="email">
					{m.email()}
					<span class="text-destructive">*</span>
				</Label>
				<Input type="email" id="email" name="email" autocomplete="email" bind:value={email} />
			</div>

			<div class="flex flex-1 flex-col gap-2">
				<Label for="password">
					{m.password()}
					<span class="text-destructive">*</span>
				</Label>
				<Input
					type="password"
					id="password"
					name="password"
					autocomplete="new-password"
					bind:value={password}
					oninput={() => {
						const trimmed = password.trim();
						errors.password = m.valid_password_length();

						if (!trimmed || trimmed.length < 8) return;

						const res = checkPasswordStrength(password);
						console.log(res);
					}}
				/>
				{#if errors.password}
					<div class="flex items-center gap-1">
						<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
						<span class="text-sm text-destructive">{errors.password}</span>
					</div>
				{/if}
			</div>

			<Button type="submit">{m.signup()}</Button>
		</form>
	</div>
</div>

<!-- <div class="flex min-h-screen items-center justify-center px-4">
	<div class="w-full max-w-md space-y-6 rounded-2xl border p-8 shadow-lg">
		<div class="text-center">
			<h1 class="text-2xl font-semibold tracking-tight">
				{m.signup()}
			</h1>
		</div>

		<form
			action="?/signup"
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
							required
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
							required
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
							required
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
							required
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
							required
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
			{m.have_an_account()}
			<a href={localizeHref('/login')} class="hover:underline hover:underline-offset-2"
				>{m.login()}</a
			>
		</div>
	</div>
</div>
 -->
