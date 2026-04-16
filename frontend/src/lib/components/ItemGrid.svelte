<script lang="ts">
	import { goto } from '$app/navigation';
	import type { FilePublic, FolderPublic } from '$lib/client';
	import { m } from '$lib/paraglide/messages';
	import { formatBytes, formatDate } from '$lib/utilities/utils';
	import ActionsButton from './ActionsButton.svelte';

	let {
		folders = $bindable(),
		files = $bindable()
	}: {
		folders?: FolderPublic[];
		files?: FilePublic[];
	} = $props();
</script>

<table class="w-full">
	<thead>
		<tr class="border-b">
			<th class="p-2 text-left">{m.name()}</th>
			<th class="p-2 text-left">{m.owner()}</th>
			<th class="p-2 text-left">{m.date_modified()}</th>
			<th class="p-2 text-left">{m.size()}</th>
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
