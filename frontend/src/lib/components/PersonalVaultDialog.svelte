<script lang="ts">
	import { verifyPasswordPost, type UserPublic } from '$lib/client';
	import * as Dialog from '$lib/components/ui/dialog';
	import { m } from '$lib/paraglide/messages';
	import { toast } from 'svelte-sonner';
	import Button from './ui/button/button.svelte';
	import Input from './ui/input/input.svelte';
	import { clientSideClient } from '$lib/utilities/client-side';
	import {
		deriveKeyFromPassword,
		encodeKey,
		encryptPrivateKeyWithPassword,
		encryptPrivateKeyWithRecovery,
		exportPrivateKey,
		exportPublicKey,
		generateRecoveryKey,
		generateRSAKeyPair,
		getRandomValues,
		importRecoveryKey
	} from '$lib/utilities/e2ee';

	let {
		open,
		user
	}: {
		open: boolean;
		user: UserPublic;
	} = $props();

	let step: number = $state(1);
	let password: string | undefined = $state();
	let recovery: string = $state('');

	function nextStep() {
		step += 1;
	}

	async function verifyPassword(password: string) {
		const { data } = await verifyPasswordPost({
			client: clientSideClient,
			query: {
				password
			},
			throwOnError: true
		});

		if (!data) {
			toast.error('Incorrect password');
			return;
		}
		await setup(password);
		nextStep();
	}

	async function setup(password: string) {
		const { publicKey, privateKey } = await generateRSAKeyPair();
		const exportedPublicKey = await exportPublicKey(publicKey);
		const exportedPrivateKey = await exportPrivateKey(privateKey);

		const recoveryBase64 = await generateRecoveryKey();
		const recoveryKey = await importRecoveryKey(recoveryBase64);
		recovery = recoveryBase64;

		const salt = getRandomValues(16);
		const derivedKey = await deriveKeyFromPassword(password, salt);

		const { iv: ivRecovery, encrypted: encryptedPrivateKeyRecovery } =
			await encryptPrivateKeyWithRecovery(privateKey, recoveryKey);
		const { iv: ivPassword, encrypted: encryptedPrivateKey } = await encryptPrivateKeyWithPassword(
			privateKey,
			derivedKey
		);

		localStorage.setItem('publicKey', encodeKey(exportedPublicKey));
		localStorage.setItem('privateKey', encodeKey(exportedPrivateKey));

		/* TODO: Send to backend the items to save */
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content showCloseButton={false} class="max-w-md">
		{#if step === 1}
			<h2 class="text-lg font-semibold">Welcome to your Personal Vault</h2>

			<p class="mt-3 text-sm text-muted-foreground">
				Your Personal Vault is a private, end-to-end encrypted space for your most sensitive files.
				Everything is encrypted directly on your device before it ever reaches our servers.
			</p>

			<p class="mt-3 text-sm text-muted-foreground">
				This ensures that only you can access your data — not the server, and not anyone else.
			</p>

			<p class="mt-3 text-sm text-muted-foreground">
				To continue, we’ll set up your encryption keys and recovery options.
			</p>

			<div class="mt-6 flex justify-end">
				<Button type="button" variant="default" onclick={nextStep}>Continue</Button>
			</div>
		{:else if step === 2}
			<h2 class="text-lg font-semibold">Confirm your password</h2>

			<p class="mt-2 text-sm text-muted-foreground">
				Enter your current password to securely initialize your Personal Vault.
			</p>

			<Input
				class="mt-4"
				type="password"
				placeholder="Enter your password"
				autocomplete="current-password"
				bind:value={password}
				required
			/>

			<div class="mt-6 flex justify-end">
				<Button
					type="button"
					variant="default"
					disabled={!password}
					onclick={async () => password && (await verifyPassword(password))}
				>
					Continue
				</Button>
			</div>
		{:else if step === 3}
			<h2 class="text-lg font-semibold">Save your recovery key</h2>

			<p class="mt-2 text-sm text-muted-foreground">
				This recovery key is the only way to restore access to your files if you forget your
				password.
			</p>

			<p class="mt-2 text-sm text-muted-foreground">
				We recommend saving it in a password manager or writing it down and storing it safely
				offline.
			</p>

			<div class="mt-4">
				<Input type="text" readonly value={recovery} class="font-mono text-xs" />
			</div>

			<p class="mt-3 text-sm text-destructive">
				If you lose both your password and this recovery key, your data cannot be recovered.
			</p>

			<div class="mt-6 flex justify-between">
				<Button
					type="button"
					variant="outline"
					onclick={() => navigator.clipboard.writeText(recovery)}
				>
					Copy
				</Button>

				<Button type="button">Download</Button>
			</div>
		{/if}
	</Dialog.Content>
</Dialog.Root>
