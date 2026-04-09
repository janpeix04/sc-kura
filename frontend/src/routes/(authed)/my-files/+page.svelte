<script lang="ts">
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
	setContext('renameItemForm', data.renameItemForm);
</script>

{#snippet children()}
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
{/snippet}

<StorageLayout user={data.user} {children} folderId={data.root!.id} />
