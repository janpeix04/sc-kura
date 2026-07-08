<script lang="ts">
	import { applyAction, enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input/index';
	import { Label } from '$lib/components/ui/label';
	import { m } from '$lib/paraglide/messages';
	import { createFormValidator } from '$lib/schemas/form-validation.svelte';
	import type { ResetPasswordFields } from '$lib/schemas/types';
	import {
		matches,
		MIN_PASSWORD_LENGTH,
		minLength,
		required,
		type ValidatorMap
	} from '$lib/schemas/validation';
	import { toast } from 'svelte-sonner';

	let password: string = $state('');
	let confirmPassword: string = $state('');

	const validators: ValidatorMap<ResetPasswordFields> = {
		password: [
			required(m.enter_a_password()),
			minLength(MIN_PASSWORD_LENGTH, m.valid_password_length())
		],
		confirmPassword: [
			required(m.confirm_your_password()),
			matches(() => password, m.passwords_do_not_match())
		]
	};

	const form = createFormValidator<ResetPasswordFields>(validators);
</script>

<div class="flex min-h-screen items-center justify-center bg-background">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-md">
		<div class="flex flex-col justify-center">
			<h1 class="text-lg font-bold">{m.reset_password_app_account({ appName: 'Kura' })}</h1>

			<div class="flex items-center gap-2 text-sm text-muted-foreground">
				<span>{m.reset_password_subtitle()}.</span>
			</div>
		</div>

		<form
			action="?/resetPassword"
			method="POST"
			class="space-y-4"
			novalidate
			use:enhance={({ cancel }) => {
				console.log('called');
				if (!form.validate({ password, confirmPassword })) {
					cancel();
				}

				return async ({ result, update }) => {
					console.log('return', result);

					if (result.type === 'success') {
						const data = result.data as { success: boolean; message: string };

						if (data.success) {
							toast.success(data.message, { duration: 5000 });
						} else {
							toast.error(data.message);
						}
					}

					await applyAction(result);
					await update();
				};
			}}
		>
			<div class="flex flex-1 flex-col gap-2">
				<Label for="password">
					{m.password()}
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

			<div class="flex flex-1 flex-col gap-2">
				<Label for="password">
					{m.password()}
				</Label>
				<Input
					type="password"
					id="password"
					name="password"
					autocomplete="new-password"
					bind:value={confirmPassword}
					class={form.errors.confirmPassword && 'border-destructive'}
					oninput={() => form.clearError('confirmPassword')}
					required
				/>
				{#if form.errors.confirmPassword}
					<div class="flex items-center gap-1">
						<span class="icon-[lucide--triangle-alert] size-3.5 text-destructive"></span>
						<p class="text-sm text-destructive">{form.errors.confirmPassword}</p>
					</div>
				{/if}
			</div>

			<Button type="submit" class="w-full">
				{m.reset_password()}
			</Button>
		</form>
	</div>
</div>
