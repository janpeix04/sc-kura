<script lang="ts">
	import * as Form from '$lib/components/ui/form/index';
	import { Input } from '$lib/components/ui/input/index';
	import { type SuperValidated, type Infer, superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { ORIGINS } from '$lib/schemas/types.js';
	import { toast } from 'svelte-sonner';
	import { loginSchema, type LoginSchema } from '$lib/schemas/auth';

	let {
		data
	}: { data: { form: SuperValidated<Infer<LoginSchema>>; origin: ORIGINS; message: string } } =
		$props();

	const form = superForm(data.form, {
		validators: zod4Client(loginSchema)
	});

	const { form: formData, enhance } = form;

	$effect(() => {
		if (data.origin === ORIGINS.Signup) {
			toast.info(data.message, { duration: 8000 });
		} else if (data.origin === ORIGINS.ResetPassword) {
			toast.info(data.message, { duration: 8000 });
		}
	});
</script>

<div class="bg-primary flex h-full w-full items-center justify-center">
	<form
		action="?/login"
		method="POST"
		class="bg-secondary w-105 rounded-3xl px-10 py-6"
		use:enhance
	>
		<div class="mb-8 text-center">
			<h2 class="text-xl font-semibold">Welcome to Kura</h2>
		</div>
		<Form.Field {form} name="username">
			<Form.Control>
				{#snippet children({ props })}
					<Form.Label>Email</Form.Label>
					<Input
						{...props}
						bind:value={$formData.username}
						type="email"
						autocomplete="email"
						placeholder="example@gmail.com"
						required
					/>
				{/snippet}
			</Form.Control>
			<Form.FieldErrors />
		</Form.Field>

		<Form.Field {form} name="password">
			<Form.Control>
				{#snippet children({ props })}
					<Form.Label>Password</Form.Label>
					<Input
						{...props}
						bind:value={$formData.password}
						type="password"
						autocomplete="new-password"
						placeholder="********"
						required
					/>
				{/snippet}
			</Form.Control>
			<Form.FieldErrors />
		</Form.Field>
		<div class="mt-3 text-right text-sm">
			<a href="/forgot/password" class="text-primary-high hover:underline hover:underline-offset-3">
				Forgot your password?
			</a>
		</div>
		<Form.Button class="mt-4 h-11 w-full cursor-pointer px-2.5" type="submit">Log in</Form.Button>
		<div class="mt-6 text-center text-sm">
			<span>
				Don't have an account?
				<a href="/signup" class="text-primary-high hover:underline hover:underline-offset-3"
					>Sign up</a
				>
			</span>
		</div>
	</form>
</div>
