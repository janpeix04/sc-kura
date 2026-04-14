<script lang="ts">
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import ItemsListLayout from '$lib/layouts/ItemsListLayout.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
	setContext('renameItemForm', data.renameItemForm);

	let folders = $state(data.folders);
	let files = $state(data.files);
</script>

{#snippet children()}
	<div class="shrink-0">
		<Breadcrumb.Root>
			<Breadcrumb.List class="text-lg">
				<Breadcrumb.Item>
					<Breadcrumb.Link href={localizeHref('/my-files')}>
						<span class="text-2xl">{m.my_files()}</span>
					</Breadcrumb.Link>
				</Breadcrumb.Item>
				<Breadcrumb.Separator class="flex" />
			</Breadcrumb.List>
		</Breadcrumb.Root>
	</div>

	
	<ItemsListLayout bind:folders bind:files />
{/snippet}

<StorageLayout user={data.user} {children} folderId={data.root!.id} />
