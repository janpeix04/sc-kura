<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Form from '$lib/components/ui/form';
	import { m } from '$lib/paraglide/messages';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import Button from './ui/button/button.svelte';
	import Input from './ui/input/input.svelte';
	import {
		verifyPasswordSchema,
		type ResetVaultPasswordSchema,
		type VerifyPasswordSchema
	} from '$lib/schemas/auth';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { toast } from 'svelte-sonner';
	import { cryptoTokenPost, cryptoUsersKeysGet } from '$lib/client';
	import { clientSideClient } from '$lib/utilities/client-side';
	import {
		base64ToArrayBuffer,
		decryptPrivateKey,
		deriveKeyFromPassword,
		importKey
	} from '$lib/crypto';
	import { publicKey as publicKeyStore, privateKey as privateKeyStore } from '$lib/stores/crypto';
	import { get } from 'svelte/store';
	import { vault } from '$lib/stores/vault';
	import PersonalVaultRecoveryDialog from './PersonalVaultRecoveryDialog.svelte';

	let {
		open = $bindable(),
		verifyPasswordForm,
		resetPasswordForm,
		cb
	}: {
		open: boolean;
		verifyPasswordForm: SuperValidated<VerifyPasswordSchema>;
		resetPasswordForm: SuperValidated<ResetVaultPasswordSchema>;
		cb: (privateKey: CryptoKey) => void;
	} = $props();

	const form = superForm(verifyPasswordForm, {
		validators: zod4Client(verifyPasswordSchema)
	});

	const { form: formData, enhance } = form;

	let forgotPassword = $state(false);

	async function getRSAKeys(password: string) {
		const { data, error } = await cryptoUsersKeysGet({
			client: clientSideClient
		});

		if (error) {
			toast.error(m.oops_something_went_wrong());
			return;
		}

		const { public_key, encrypted_private_key, pbkdf2_salt, iv: ivBase64 } = data;

		const publicKeyBuffer = base64ToArrayBuffer(public_key);
		const publicKey = await importKey(
			'spki',
			publicKeyBuffer,
			{ name: 'RSA-OAEP', hash: 'SHA-512' },
			true,
			['wrapKey']
		);

		const encryptedPrivateKeyBuffer = base64ToArrayBuffer(encrypted_private_key);

		const salt = base64ToArrayBuffer(pbkdf2_salt);
		const passwordKey = await deriveKeyFromPassword(password, salt);
		const iv = base64ToArrayBuffer(ivBase64);
		const privateKeyBuffer = await decryptPrivateKey(passwordKey, iv, encryptedPrivateKeyBuffer);
		const privateKey = await importKey(
			'pkcs8',
			privateKeyBuffer,
			{ name: 'RSA-OAEP', hash: 'SHA-512' },
			true,
			['unwrapKey']
		);

		publicKeyStore.set(publicKey);
		privateKeyStore.set(privateKey);
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content
		showCloseButton={false}
		onInteractOutside={(e) => e.preventDefault()}
		onEscapeKeydown={(e) => e.preventDefault()}
		class="sm:max-w-md"
	>
		<form
			action="?/verifyPassword"
			method="POST"
			class="flex flex-col gap-4"
			use:enhance={{
				async onResult({ result }) {
					if (result.type === 'failure') {
						const form = result.data?.form;

						if (form.message) {
							toast.error(form.message);
						}
					}

					if (result.type === 'success') {
						const form = result.data?.form;

						const correct = form.message;

						if (correct) {
							const { data, error } = await cryptoTokenPost({
								client: clientSideClient
							});

							if (!error) {
								$vault.token = data.access_token;
								$vault.expiresAt = Date.now() + 30 * 60 * 1000;
								$vault.locked = false;
							}

							let pub = get(publicKeyStore);
							let priv = get(privateKeyStore);

							if (!pub || !priv) {
								await getRSAKeys($formData.password);

								pub = get(publicKeyStore);
								priv = get(privateKeyStore);
							}

							if (priv) cb(priv);
							open = false;
						} else {
							toast.error(m.incorrect_password());
						}
					}
				}
			}}
		>
			<div class="flex flex-col gap-1">
				<h2 class="text-lg font-semibold">{m.enter_your_passowrd()}</h2>
				<p class="text-sm text-muted-foreground">
					{m.enter_your_password_description()}
				</p>
			</div>

			<Form.Field {form} name="password">
				<Form.Control>
					{#snippet children({ props })}
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

			<div class="flex items-center justify-between">
				<Button
					variant="link"
					class="text-sm text-muted-foreground underline hover:text-foreground"
					onclick={() => {
						forgotPassword = true;
						open = false;
					}}
				>
					{m.forgot_password()}
				</Button>

				<Button type="submit">
					{m.continue()}
				</Button>
			</div>
		</form>
	</Dialog.Content>
</Dialog.Root>

<PersonalVaultRecoveryDialog bind:open={forgotPassword} {resetPasswordForm} />
