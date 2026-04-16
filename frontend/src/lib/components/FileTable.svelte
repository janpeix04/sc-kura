<script lang="ts">
	import { goto } from '$app/navigation';
	import type { FilePublic, FolderPublic } from '$lib/client';
	import { m } from '$lib/paraglide/messages';
	import type { SortKeys } from '$lib/schemas/types';
	import { formatBytes, formatDate } from '$lib/utilities/utils';
	import ActionsButton from './ActionsButton.svelte';

	let {
		folders = $bindable(),
		files = $bindable()
	}: {
		folders?: FolderPublic[];
		files?: FilePublic[];
	} = $props();

	let sortKey = $state<SortKeys | undefined>();
	let sortDir = $state<'asc' | 'desc'>('asc');

	function toggleSort(key: typeof sortKey) {
		if (sortKey === key) {
			sortDir = sortDir === 'asc' ? 'desc' : 'asc';
		} else {
			sortKey = key;
			sortDir = 'asc';
		}

		applySort();
	}

	function applyFileSort() {
		if (!files) return;

		files = [...files].sort((a, b) => compare(a, b));
	}

	function applyFolderSort() {
		if (!folders) return;

		folders = [...folders].sort((a, b) => compare(a, b));
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
		applyFileSort();
		applyFolderSort();
	}

	function isActive(key: SortKeys) {
		return sortKey === key;
	}
</script>

<table class="mt-2 w-full">
	<thead>
		<tr class="cursor-pointer border-b">
			<th class="rounded-t-lg p-2 text-left hover:bg-hover" onclick={() => toggleSort('name')}>
				<span class="flex items-center gap-1">
					{m.name()}
					<span
						class={`icon-[lucide--chevron-down] size-4 transition-all duration-200 ${
							isActive('name') ? 'opacity-100' : 'opacity-0'
						} ${isActive('name') && sortDir === 'asc' ? 'rotate-180' : ''}`}
					></span>
				</span>
			</th>

			<th class="rounded-t-lg p-2 text-left hover:bg-hover" onclick={() => toggleSort('owner')}>
				<span class="flex items-center gap-1">
					{m.owner()}
					<span
						class={`icon-[lucide--chevron-down] size-4 transition-all duration-200 ${
							isActive('owner') ? 'opacity-100' : 'opacity-0'
						} ${isActive('owner') && sortDir === 'asc' ? 'rotate-180' : ''}`}
					></span>
				</span>
			</th>

			<th
				class="rounded-t-lg p-2 text-left hover:bg-hover"
				onclick={() => toggleSort('date_modified')}
			>
				<span class="flex items-center gap-1">
					{m.date_modified()}
					<span
						class={`icon-[lucide--chevron-down] size-4 transition-all duration-200 ${
							isActive('date_modified') ? 'opacity-100' : 'opacity-0'
						} ${isActive('date_modified') && sortDir === 'asc' ? 'rotate-180' : ''}`}
					></span>
				</span>
			</th>

			<th class="rounded-t-lg p-2 text-left hover:bg-hover" onclick={() => toggleSort('size')}>
				<span class="flex items-center gap-1">
					{m.size()}
					<span
						class={`icon-[lucide--chevron-down] size-4 transition-all duration-200 ${
							isActive('size') ? 'opacity-100' : 'opacity-0'
						} ${isActive('size') && sortDir === 'asc' ? 'rotate-180' : ''}`}
					></span>
				</span>
			</th>

			<th class="p-2"></th>
		</tr>
	</thead>

	<tbody>
		{#each folders as folder (folder.id)}
			<tr
				class="group cursor-pointer border-b hover:bg-hover"
				onclick={() => goto(`/folder/${folder.id}`)}
			>
				<td class="flex items-center gap-2 p-2">
					<span class="icon-[lucide--folder] size-5"></span>
					{folder.name}
				</td>
				<td class="p-2">{folder.owner}</td>
				<td class="p-2">{formatDate(folder.modified_at)}</td>
				<td class="p-2">{formatBytes(folder.size)}</td>
				<td class="flex items-center justify-end p-2">
					<ActionsButton item={folder} />
				</td>
			</tr>
		{/each}

		{#each files as file (file.id)}
			<tr class="group cursor-pointer border-b hover:bg-hover">
				<td class="flex items-center gap-2 p-2">
					<span class="icon-[lucide--file] size-5"></span>
					{file.name}
				</td>
				<td class="p-2">{file.owner}</td>
				<td class="p-2">{formatDate(file.modified_at)}</td>
				<td class="p-2">{formatBytes(file.size)}</td>
				<td class="flex items-center justify-end p-2">
					<ActionsButton item={file} />
				</td>
			</tr>
		{/each}
	</tbody>
</table>
