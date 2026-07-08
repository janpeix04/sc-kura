<script lang="ts">
	import { applyAction, enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime.js';
	import { createFormValidator } from '$lib/schemas/form-validation.svelte.js';
	import { ORIGINS, type LoginFields } from '$lib/schemas/types';
	import { EMAIL_REGEX, pattern, required, type ValidatorMap } from '$lib/schemas/validation.js';
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	let { data } = $props();

	let email: string = $state('');
	let password: string = $state('');

	let error: string = $state('');

	const validators: ValidatorMap<LoginFields> = {
		email: [
			required(m.please_enter_a_valid_email_address()),
			pattern(EMAIL_REGEX, m.please_enter_a_valid_email_address())
		],
		password: [required(m.enter_a_password())]
	};

	const form = createFormValidator<LoginFields>(validators);

	onMount(() => {
		if (data.origin === ORIGINS.Signup) {
			toast.info(data.message, { duration: 5000 });
		}
		if (data.origin === ORIGINS.ResetPassword) {
			toast.success(data.message);
		}
	});
</script>

<div class="flex min-h-screen items-center justify-center bg-background">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-md">
		<h1 class="text-lg font-bold">{m.login_to_your_app_account({ appName: 'Kura' })}</h1>

		<form
			action="?/login"
			method="POST"
			class="space-y-6"
			use:enhance={({ cancel }) => {
				error = '';
				if (!form.validate({ email, password })) {
					cancel();
				}

				return async ({ result, update }) => {
					if (result.type === 'success') {
						const data = result.data as {
							success: boolean;
							message: string;
							loc: string | undefined;
						};

						if (!data.success) {
							if (data.loc && data.loc === 'toast') {
								toast.info(data.message);
							} else {
								error = data.message;
							}
							password = '';
							return;
						}
					}

					await applyAction(result);
					await update();
				};
			}}
		>
			<div class="flex flex-1 flex-col gap-2">
				<Label for="email">
					{m.email()}
					<span class="text-destructive">*</span>
				</Label>
				<Input
					type="email"
					id="email"
					name="email"
					autocomplete="email"
					bind:value={email}
					class={form.errors.email && 'border-destructive'}
					oninput={() => form.clearError('email')}
					required
				/>
				{#if form.errors.email}
					<div class="flex items-center gap-1">
						<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
						<p class="text-sm text-destructive">{form.errors.email}</p>
					</div>
				{/if}
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
					class={form.errors.password && 'border-destructive'}
					oninput={() => form.clearError('password')}
					required
				/>
				{#if form.errors.password}
					<div class="flex items-center gap-1">
						<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
						<p class="text-sm text-destructive">{form.errors.password}</p>
					</div>
				{/if}
			</div>

			{#if error}
				<div class="flex flex-1 items-center gap-2 rounded-md bg-destructive p-2">
					<span class="icon-[lucide--triangle-alert] size-3.5 shrink-0 text-white"></span>
					<span class="text-sm text-white">{error}</span>
				</div>
			{/if}

			<div
				class="text-right text-sm font-semibold text-muted-foreground underline underline-offset-2"
			>
				<a href={localizeHref('/forgot/password')}>{m.forgot_password()}</a>
			</div>

			<Button type="submit" class="w-full">{m.login()}</Button>

			<div class="flex items-center justify-center gap-2 text-sm text-muted-foreground">
				<span>{m.dont_have_an_account()}</span>
				<a href={localizeHref('/signup')} class="font-semibold underline underline-offset-2">
					{m.signup()}
				</a>
			</div>
		</form>
	</div>
</div>

<!-- <div class="flex min-h-screen items-center justify-center bg-gray-50 px-4">
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
							autocomplete="email"
							bind:value={$formData.username}
							required
						/>wd
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
							required
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
				>Create acount</a
			>
		</div>
	</div>
</div>
 -->
