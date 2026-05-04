<script lang="ts">
	import { page } from '$app/state';
	import { cryptoFolderFolderIdPost, storageFolderIdPost } from '$lib/client';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { arrayBufferToBase64, encryptFile, generateAESKey, wrapKey } from '$lib/crypto';
	import { m } from '$lib/paraglide/messages';
	import { publicKey } from '$lib/stores/crypto';
	import { clientSideClient } from '$lib/utilities/client-side';
	import { toast } from 'svelte-sonner';
	import { get } from 'svelte/store';
	import { Button } from './ui/button';
	import { invalidatePage } from '$lib/utilities/utils';
	import { tick } from 'svelte';

	let {
		open = $bindable(),
		folderId
	}: {
		open: boolean;
		folderId: string;
	} = $props();

	let newName: string = $state(m.untitled_folder());
	let isPersonalVault = $derived(page.url.pathname.includes('/personal-vault'));
	let inputElement: HTMLInputElement | null = $state(null);

	function createFolder(name: string, folderId: string, isEncrypted: boolean) {
		const creations = [];

		if (isEncrypted) {
			creations.push(createEncryptedFolder(name, folderId));
		} else {
			creations.push(createStorageFolder(name, folderId));
		}

		return Promise.all(creations);
	}

	async function createStorageFolder(name: string, folderId: string) {
		const { data, error } = await storageFolderIdPost({
			client: clientSideClient,
			path: {
				folder_id: folderId
			},
			body: {
				name
			}
		});

		if (!error) {
			toast.success(data);
		}

		if (error === undefined) return;

		if ('msg' in error) {
			toast.error(error.msg);
		}

		toast.error(m.oops_something_went_wrong());
	}

	async function createEncryptedFolder(name: string, folderId: string) {
		const key = await generateAESKey();
		const encodedName = new TextEncoder().encode(name);
		const { iv, encrypted } = await encryptFile(key, encodedName.buffer);

		const pub = get(publicKey);

		if (!pub) {
			toast.error(m.oops_something_went_wrong());
			return;
		}

		const encryptedKey = await wrapKey(key, pub);

		const { data, error } = await cryptoFolderFolderIdPost({
			client: clientSideClient,
			path: {
				folder_id: folderId
			},
			body: {
				encrypted_key: arrayBufferToBase64(encryptedKey),
				encrypted_name: arrayBufferToBase64(encrypted),
				iv: arrayBufferToBase64(iv)
			}
		});

		if (!error) {
			toast.success(data);
		}

		if (error === undefined) return;

		if ('msg' in error) {
			toast.error(error.msg);
		}

		toast.error(m.oops_something_went_wrong());
	}

	$effect(() => {
		if (!open || !inputElement) return;

		tick().then(() => {
			inputElement?.focus();
			inputElement?.select();
		});
	});
</script>

<Dialog.Root bind:open>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>{m.new_folder()}</Dialog.Title>
		</Dialog.Header>

		<Input bind:ref={inputElement} data-autofocus type="text" bind:value={newName} />

		<div class="flex justify-end gap-2">
			<Button
				type="button"
				variant="outline"
				onclick={() => {
					open = false;
				}}
			>
				{m.cancel()}
			</Button>
			<Button
				type="button"
				onclick={() => {
					if (!newName) newName = m.new_folder();
					createFolder(newName, folderId, isPersonalVault).finally(() => {
						invalidatePage();
						open = false;
					});
				}}>{m.create()}</Button
			>
		</div>
	</Dialog.Content>
</Dialog.Root>
