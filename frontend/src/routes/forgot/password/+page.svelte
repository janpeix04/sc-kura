<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input/index';
	import { Label } from '$lib/components/ui/label';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { createFormValidator } from '$lib/schemas/form-validation.svelte';
	import type { ForgotPasswordFields } from '$lib/schemas/types';
	import { EMAIL_REGEX, pattern, required, type ValidatorMap } from '$lib/schemas/validation';
	import { toast } from 'svelte-sonner';

	let email: string = $state('');

	const validators: ValidatorMap<ForgotPasswordFields> = {
		email: [
			required(m.please_enter_a_valid_email_address()),
			pattern(EMAIL_REGEX, m.please_enter_a_valid_email_address())
		]
	};

	const form = createFormValidator<ForgotPasswordFields>(validators);
</script>

<div class="flex min-h-screen items-center justify-center bg-background">
	<div class="w-full max-w-md space-y-6 rounded-2xl border bg-white p-8 shadow-md">
		<div class="flex flex-col justify-center">
			<h1 class="text-lg font-bold">{m.recover_access_to_your_app_account({ appName: 'Kura' })}</h1>

			<div class="flex items-center gap-2 text-sm text-muted-foreground">
				<span>{m.forgot_password_subtitle()}.</span>
			</div>
		</div>
		<form
			action="?/forgotPassword"
			method="POST"
			class="space-y-4"
			use:enhance={({ cancel }) => {
				if (!form.validate({ email })) {
					cancel();
				}

				return async ({ result, update }) => {
					if (result.type === 'success') {
						const data = result.data as { success: boolean; message: string };

						if (data.success) {
							toast.info(data.message);
						}
					}
					await update();
				};
			}}
		>
			<div class="flex flex-1 flex-col gap-2">
				<Label for="email">
					{m.email()}
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

			<Button type="submit" class="w-full">
				{m.start()}
			</Button>
		</form>

		<div class="text-center text-sm font-semibold text-muted-foreground">
			<a href={localizeHref('/login')} class="hover:underline hover:underline-offset-2">
				{m.login()}
			</a>
		</div>
	</div>
</div>
