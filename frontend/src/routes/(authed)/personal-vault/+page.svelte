<script lang="ts">
	import * as Breadcrumb from '$lib/components/ui/breadcrumb';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
</script>

{#snippet children()}
    <Breadcrumb.Root>
		<Breadcrumb.List class="text-lg text-foreground">
			<Breadcrumb.Item>
				<span class="text-2xl">{m.personal_vault()}</span>
			</Breadcrumb.Item>
		</Breadcrumb.List>
	</Breadcrumb.Root>
{/snippet}

<StorageLayout
	user={data.user}
	folderId={data.root!.id}
	availableSpace={data.availableSpace}
	{children}
/>
