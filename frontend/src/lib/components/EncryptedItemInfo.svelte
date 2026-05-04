<script lang="ts">
	import type { FolderPublic } from '$lib/client';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import type { DecryptedFolder } from '$lib/schemas/types';
	import { formatBytes, formatDate } from '$lib/utilities/utils';

	let {
		open = $bindable(),
		item
	}: {
		open: boolean;
		item: DecryptedFolder;
	} = $props();
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="w-105">
		<Dialog.Header class="space-y-3">
			<div class="flex items-center gap-3">
				<div class="flex size-10 items-center justify-center rounded-lg bg-muted">
					{#if item.type === 'directory'}
						<span class="icon-[lucide--folder] size-5 bg-gray-600"></span>
					{:else}
						<span class="icon-[lucide--file] size-5 bg-gray-600"></span>
					{/if}
				</div>
				<div>
					<Dialog.Title class="wrap-break-words max-w-75 text-lg font-semibold">
						<span class="block max-w-full truncate">
							{item.name}
						</span>
					</Dialog.Title>
					<p class="text-sm text-muted-foreground">
						{item.type === 'directory' ? m.folder_details() : m.file_details()}
					</p>
				</div>
			</div>
		</Dialog.Header>

		<div class="mt-6 space-y-4 text-sm">
			<div class="grid grid-cols-3 gap-2">
				<span class="col-span-1 text-muted-foreground">{m.size()}</span>
				<span class="col-span-2 font-medium">{formatBytes(item.size)}</span>
			</div>

			<div class="grid grid-cols-3 gap-2">
				<span class="col-span-1 text-muted-foreground">{m.type()}</span>
				<span class="col-span-2 font-medium">{item.type}</span>
			</div>

			<div class="grid grid-cols-3 gap-2">
				<span class="col-span-1 text-muted-foreground">{m.modified()}</span>
				<span class="col-span-2 font-medium">{formatDate(item.createdAt)}</span>
			</div>
		</div>
	</Dialog.Content>
</Dialog.Root>
