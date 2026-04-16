<script lang="ts">
	import { goto } from '$app/navigation';
	import type { FilePublic, FolderPublic } from '$lib/client';
	import { m } from '$lib/paraglide/messages';
	import type { SortKeys } from '$lib/schemas/types';
	import { formatBytes, formatDate } from '$lib/utilities/utils';
	import ActionsButton from './ActionsButton.svelte';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';

	let {
		folders = $bindable(),
		files = $bindable()
	}: {
		folders?: FolderPublic[];
		files?: FilePublic[];
	} = $props();

	let sortKey = $state<SortKeys | undefined>();
	let sortDir = $state<'asc' | 'desc'>('asc');

	function toggleSort(key: SortKeys) {
		if (sortKey === key) {
			sortDir = sortDir === 'asc' ? 'desc' : 'asc';
		} else {
			sortKey = key;
			sortDir = 'asc';
		}

		applySort();
	}

	function compare(a: any, b: any) {
		let result = 0;

		switch (sortKey) {
			case 'name':
				result = a.name.localeCompare(b.name);
				break;
			case 'owner':
				result = a.owner.localeCompare(b.owner);
				break;
			case 'date_modified':
				result = new Date(a.modified_at).getTime() - new Date(b.modified_at).getTime();
				break;
			case 'size':
				result = a.size - b.size;
				break;
		}

		return sortDir === 'asc' ? result : -result;
	}

	function applySort() {
		if (files) files = [...files].sort(compare);
		if (folders) folders = [...folders].sort(compare);
	}

	function isActive(key: SortKeys) {
		return sortKey === key;
	}
</script>

<ScrollArea class="h-full w-full py-2">
	<table class="w-full border-collapse">
		<thead class="sticky top-0 z-20">
			<tr class="border-b bg-white">
				<th
					class="cursor-pointer rounded-t-md px-4 py-3 text-left transition hover:bg-muted"
					onclick={() => toggleSort('name')}
				>
					<span class="flex items-center gap-2">
						{m.name()}

						<span
							class={`icon-[lucide--chevron-down] size-4 transition-all duration-200 ${
								isActive('name') ? 'opacity-100' : 'opacity-0'
							} ${isActive('name') && sortDir === 'asc' ? 'rotate-180' : ''}`}
						></span>
					</span>
				</th>

				<th
					class="cursor-pointer rounded-t-md px-4 py-3 text-left transition hover:bg-muted"
					onclick={() => toggleSort('owner')}
				>
					<span class="flex items-center gap-2">
						{m.owner()}

						<span
							class={`icon-[lucide--chevron-down] size-4 transition-all duration-200 ${
								isActive('owner') ? 'opacity-100' : 'opacity-0'
							} ${isActive('owner') && sortDir === 'asc' ? 'rotate-180' : ''}`}
						></span>
					</span>
				</th>

				<th
					class="cursor-pointer rounded-t-md px-4 py-3 text-left transition hover:bg-muted"
					onclick={() => toggleSort('date_modified')}
				>
					<span class="flex items-center gap-2">
						{m.date_modified()}

						<span
							class={`icon-[lucide--chevron-down] size-4 transition-all duration-200 ${
								isActive('date_modified') ? 'opacity-100' : 'opacity-0'
							} ${isActive('date_modified') && sortDir === 'asc' ? 'rotate-180' : ''}`}
						></span>
					</span>
				</th>

				<th
					class="cursor-pointer rounded-t-md px-4 py-3 text-left transition hover:bg-muted"
					onclick={() => toggleSort('size')}
				>
					<span class="flex items-center gap-2">
						{m.size()}

						<span
							class={`icon-[lucide--chevron-down] size-4 transition-all duration-200 ${
								isActive('size') ? 'opacity-100' : 'opacity-0'
							} ${isActive('size') && sortDir === 'asc' ? 'rotate-180' : ''}`}
						></span>
					</span>
				</th>

				<th class="px-4 py-3"></th>
			</tr>
		</thead>

		<tbody>
			{#each folders as folder (folder.id)}
				<tr
					class="group cursor-pointer border-b transition hover:bg-muted"
					onclick={() => goto(`/folder/${folder.id}`)}
				>
					<td class="flex items-center gap-2 px-4 py-3">
						<span class="icon-[lucide--folder] size-5"></span>
						{folder.name}
					</td>
					<td class="px-4 py-3">{folder.owner}</td>
					<td class="px-4 py-3">{formatDate(folder.modified_at)}</td>
					<td class="px-4 py-3">{formatBytes(folder.size)}</td>
					<td class="flex justify-end px-4 py-3">
						<ActionsButton item={folder} />
					</td>
				</tr>
			{/each}

			{#each files as file (file.id)}
				<tr class="group cursor-pointer border-b transition hover:bg-muted">
					<td class="flex items-center gap-2 px-4 py-3">
						<span class="icon-[lucide--file] size-5"></span>
						{file.name}
					</td>
					<td class="px-4 py-3">{file.owner}</td>
					<td class="px-4 py-3">{formatDate(file.modified_at)}</td>
					<td class="px-4 py-3">{formatBytes(file.size)}</td>
					<td class="flex justify-end px-4 py-3">
						<ActionsButton item={file} />
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</ScrollArea>
