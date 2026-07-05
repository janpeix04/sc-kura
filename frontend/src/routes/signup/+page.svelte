<script lang="ts">
	import { enhance } from '$app/forms';
	import Button from '$lib/components/ui/button/button.svelte';
	import { Input } from '$lib/components/ui/input';
	import Label from '$lib/components/ui/label/label.svelte';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { createFormValidator } from '$lib/schemas/form-validation.svelte';
	import type { FieldName, PasswordFeedback } from '$lib/schemas/types';
	import { minLength, pattern, required, type ValidatorMap } from '$lib/schemas/validation';
	import { checkPasswordStrength } from '$lib/utilities/password-strength';

	const NAME_REGEX = /^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$/;
	const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	const MIN_PASSWORD_LENGTH = 8;

	const PASSWORD_TIPS = [
		'Upper and lower case letters',
		'At least one number or special character'
	];

	const STRENGTH_FEEDBACK: Record<number, Omit<PasswordFeedback, 'tips'>> = {
		0: { type: 'error', message: 'This password is too weak.' },
		1: {
			type: 'warning',
			message: 'Your password is good enough to proceed, but strengthening it is recommended.'
		},
		2: { type: 'success', message: 'This is a medium-strength password.' },
		3: { type: 'success', message: 'This is a strong password.' }
	};

	let firstName: string = $state('');
	let lastName: string = $state('');
	let email: string = $state('');
	let password: string = $state('');

	let passwordFeedback = $state<PasswordFeedback>({ type: null, message: '' });

	const validators: ValidatorMap<FieldName> = {
		firstName: [
			required('First name is required'),
			pattern(NAME_REGEX, 'First name can only contain letters')
		],
		lastName: [pattern(NAME_REGEX, 'Last name can only contain letters')],
		email: [required('Email is required'), pattern(EMAIL_REGEX, 'Please enter a valid email')],
		password: [
			required('Password is required'),
			minLength(MIN_PASSWORD_LENGTH, m.valid_password_length())
		]
	};

	const form = createFormValidator<FieldName>(validators);

	function getPasswordFeedback(value: string): PasswordFeedback {
		const trimmed = value.trim();

		if (!trimmed) return { type: null, message: '' };

		if (trimmed.length < MIN_PASSWORD_LENGTH) {
			return { type: 'error', message: m.valid_password_length() };
		}

		const { id } = checkPasswordStrength(trimmed);
		const base = STRENGTH_FEEDBACK[id] ?? { type: null, message: '' };

		return { ...base, tips: id <= 1 ? PASSWORD_TIPS : undefined };
	}

	function updatePasswordFeedback() {
		passwordFeedback = getPasswordFeedback(password);
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-background">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-md">
		<div class="flex flex-col justify-center">
			<h1 class="text-lg font-bold">{m.create_new_free_account({ appName: 'Kura' })}</h1>

			<div class="flex items-center gap-2 text-sm text-muted-foreground">
				<span>{m.have_an_account()}</span>
				<a href={localizeHref('/login')} class="font-semibold underline underline-offset-2">
					{m.login()}
				</a>
			</div>
		</div>

		<form
			action="?/signup"
			method="POST"
			class="space-y-6"
			use:enhance={({ cancel }) => {
				if (!form.validate({ firstName, lastName, email, password })) {
					cancel();
				}

				passwordFeedback = form.errors.password
					? { type: 'error', message: form.errors.password }
					: getPasswordFeedback(password);
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
						autocomplete="given-name"
						bind:value={firstName}
						class={form.errors.firstName && 'border-destructive'}
						oninput={() => form.clearError('firstName')}
						required
					/>
					{#if form.errors.firstName}
						<div class="flex items-center gap-1">
							<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
							<p class="text-sm text-destructive">{form.errors.firstName}</p>
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
						autocomplete="family-name"
						bind:value={lastName}
						class={form.errors.lastName && 'border-destructive'}
						oninput={() => form.clearError('lastName')}
					/>
					{#if form.errors.lastName}
						<div class="flex items-center gap-1">
							<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
							<p class="text-sm text-destructive">{form.errors.lastName}</p>
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
					oninput={() => {
						form.clearError('password');
						updatePasswordFeedback();
					}}
					required
				/>

				{#if passwordFeedback.type}
					<div class="flex flex-col gap-2">
						<div class="flex items-center gap-1">
							{#if passwordFeedback.type === 'error'}
								<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
								<span class="text-sm text-destructive">{passwordFeedback.message}</span>
							{:else if passwordFeedback.type === 'warning'}
								<span class="icon-[lucide--circle-alert] size-3.5 text-yellow-500"></span>
								<span class="text-sm text-yellow-500">{passwordFeedback.message}</span>
							{:else if passwordFeedback.type === 'success'}
								<span class="icon-[lucide--circle-check] size-3.5 text-green-300"></span>
								<span class="text-sm text-green-300">{passwordFeedback.message}</span>
							{/if}
						</div>

						{#if passwordFeedback.tips}
							<div class="flex flex-col gap-2">
								<span class="text-sm font-bold">Strongest passwords have:</span>
								<ul class="flex list-disc flex-col gap-2 ps-5 text-sm">
									{#each passwordFeedback.tips as tip, idx (idx)}
										<li>{tip}</li>
									{/each}
								</ul>
							</div>
						{/if}
					</div>
				{/if}
			</div>

			<Button type="submit" class="w-full">{m.signup()}</Button>
		</form>
	</div>
</div>
