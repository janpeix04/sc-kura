<script lang="ts">
	import type { Breadcrumbs } from '$lib/client/types.gen.js';
	import ActionsButton from '$lib/components/ActionsButton.svelte';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { localizeHref } from '$lib/paraglide/runtime.js';
	import { formatBytes, formatDate } from '$lib/utilities/utils.js';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
	setContext('renameItemForm', data.renameItemForm);

	let breadcrumbs = $derived(data.breadcrumbs as Breadcrumbs[]);
	let folders = $derived(data.folders);
</script>

{#snippet children()}
	<Breadcrumb {breadcrumbs} />

	<div class="mt-4 flex items-center gap-4 border-b border-gray-200 pb-2 text-sm font-semibold">
		<div class="flex-1">Name</div>
		<div class="w-48">{m.owner()}</div>
		<div class="w-36">Date modified</div>
		<div class="w-24 text-right">{m.size()}</div>
		<div class="w-8"></div>
	</div>

	{#each folders as folder}
		<div
			class="flex cursor-pointer items-center gap-4 border-b border-gray-100 py-2 hover:bg-gray-50"
		>
			<a class="flex flex-1 items-center gap-4" href={localizeHref(`/folder/${folder.id}`)}>
				<div class="flex flex-1 items-center gap-2">
					<span class="icon-[lucide--folder] size-5"></span>
					{folder.name}
				</div>
				<div class="w-48">
					<span class="text-sm">{folder.owner}</span>
				</div>
				<div class="w-36">
					<span class="text-sm">{formatDate(folder.modified_at)}</span>
				</div>
				<div class="w-24 text-right">
					<span class="text-sm">{formatBytes(folder.size)}</span>
				</div>
			</a>
			<div class="w-8">
				<ActionsButton item={folder} />
			</div>
		</div>
	{/each}
{/snippet}

<StorageLayout user={data.user} {children} />
