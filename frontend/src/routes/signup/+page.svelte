<script lang="ts">
	import { enhance } from '$app/forms';
	import Button from '$lib/components/ui/button/button.svelte';
	import { Input } from '$lib/components/ui/input';
	import Label from '$lib/components/ui/label/label.svelte';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import type { FormErrors } from '$lib/schemas/types';
	import { checkPasswordStrength } from '$lib/utilities/password-strength';

	let firstName: string = $state('');
	let lastName: string = $state('');
	let email: string = $state('');
	let password: string = $state('');

	let errors: FormErrors = $state({});

	let passwordFeedback = $state<{
		type: 'error' | 'warning' | 'success' | null;
		message: string;
	}>({
		type: null,
		message: ''
	});

	const nameRegex = /^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$/;
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

	function updatePasswordFeedback() {
		const trimmed = password.trim();

		passwordFeedback = {
			type: null,
			message: ''
		};

		if (!trimmed) return;

		if (trimmed.length < 8) {
			passwordFeedback = {
				type: 'error',
				message: m.valid_password_length()
			};
			return;
		}

		switch (checkPasswordStrength(trimmed).id) {
			case 0:
				passwordFeedback = {
					type: 'error',
					message: 'This password is too weak.'
				};
				break;

			case 1:
				passwordFeedback = {
					type: 'warning',
					message: 'Your password is good enough to proceed, but strengthening it is recommended.'
				};
				break;

			case 2:
				passwordFeedback = {
					type: 'success',
					message: 'This is a medium-strength password.'
				};
				break;

			case 3:
				passwordFeedback = {
					type: 'success',
					message: 'This is a strong password.'
				};
				break;
		}
	}

	function validateForm() {
		const newErrors: FormErrors = {};

		if (!firstName.trim()) {
			newErrors.firstName = 'First name is required';
		} else if (!nameRegex.test(firstName.trim())) {
			newErrors.firstName = 'First name can only contain letters';
		}

		if (lastName.trim() && !nameRegex.test(lastName.trim())) {
			newErrors.lastName = 'Last name can only contain letters';
		}

		if (!email.trim()) {
			newErrors.email = 'Email is required';
		} else if (!emailRegex.test(email.trim())) {
			newErrors.email = 'Please enter a valid email';
		}

		if (!password.trim()) {
			newErrors.password = 'Password is required';
		} else if (password.length < 8) {
			newErrors.password = m.valid_password_length();
		}

		errors = newErrors;

		return Object.keys(newErrors).length === 0;
	}

	function clearErrors(field: keyof FormErrors) {
		if (errors[field]) {
			errors = { ...errors, [field]: undefined };
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-background">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-md">
		<div class="flex flex-col justify-center">
			<h1 class="text-lg font-bold">{m.create_new_free_account({ appName: 'Kura' })}</h1>

			<div class="flex items-center gap-2 text-sm text-muted-foreground">
				<span>{m.have_an_account()}</span>
				<a href={localizeHref('/login')} class="font-semibold underline underline-offset-2"
					>{m.login()}</a
				>
			</div>
		</div>

		<form
			action="?/signup"
			method="POST"
			class="space-y-6"
			use:enhance={({ cancel }) => {
				if (!validateForm()) {
					cancel();
				}
			}}
		>
			<div class="flex items-start gap-2">
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
						class={errors.firstName && 'border-destructive'}
						oninput={() => clearErrors('firstName')}
					/>
					{#if errors.firstName}
						<div class="flex items-center gap-1">
							<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
							<p class="text-sm text-destructive">
								{errors.firstName}
							</p>
						</div>
					{/if}
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
						class={errors.lastName && 'border-destructive'}
						oninput={() => clearErrors('lastName')}
					/>
					{#if errors.lastName}
						<div class="flex items-center gap-1">
							<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
							<p class="text-sm text-destructive">
								{errors.lastName}
							</p>
						</div>
					{/if}
				</div>
			</div>

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
					class={errors.email && 'border-destructive'}
					oninput={() => clearErrors('email')}
				/>
				{#if errors.email}
					<div class="flex items-center gap-1">
						<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
						<p class="text-sm text-destructive">
							{errors.email}
						</p>
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
					class={errors.password && 'border-destructive'}
					oninput={() => {
						clearErrors('password');
						updatePasswordFeedback();
					}}
				/>
				{#if errors.password}
					<div class="flex items-center gap-1">
						<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
						<p class="text-sm text-destructive">
							{errors.password}
						</p>
					</div>
				{/if}
				<div class="flex items-center gap-1">
					{#if passwordFeedback.type === 'error'}
						<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
						<span class="text-sm text-destructive">{passwordFeedback.message}</span>
					{:else if passwordFeedback.type === 'warning'}
						<div class="flex flex-col gap-2">
							<span class="  text-sm text-yellow-500">
								<span class="icon-[lucide--circle-alert] size-3.5 text-yellow-500"></span>
								{passwordFeedback.message}
							</span>

							<span class="text-sm font-bold">Strongest passwords have:</span>
							<ul class="flex list-disc flex-col gap-2 text-sm">
								<li>Upper and lower case letters</li>
								<li>At least one number or special character</li>
							</ul>
						</div>
					{:else if passwordFeedback.type === 'success'}
						<span class="icon-[lucide--circle-check] size-3.5 text-green-300"></span>
						<span class="text-sm text-green-300">{passwordFeedback.message}</span>
					{/if}
				</div>
			</div>

			<Button type="submit" class="w-full">{m.signup()}</Button>
		</form>
	</div>
</div>
