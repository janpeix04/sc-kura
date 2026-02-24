<script lang="ts">
    
	import { Folder, File } from "@lucide/svelte";
	import { Button } from "./ui/button";
	import type { FileFolderPublic } from "$lib/client";
	import { formatBytes } from "$lib/utilities/storage";
	import StorageItemActions from "./StorageItemActions.svelte";
	import type { StorageMode } from "$lib/schemas/types";

    let {
        item,
        segments,
        basePath,
        mode = 'storage',
        onClick,
        onRestore,
		onDelete,
		onDownload,
		onRename,
		onInfo,
		onRecycleBin
    }: {
        item: FileFolderPublic;
        segments: string[];
        basePath?: string;
        mode?: StorageMode;
        onClick?: () => void;
        onRestore?: () => void;
		onDelete?: () => void;
		onDownload?: () => void;
		onRename?: () => void;
		onInfo?: () => void;
		onRecycleBin?: (item_id: string) => void;
    } = $props();

    let href = $derived(item.type === 'directory' && basePath ? `${basePath}/${[...segments, item.name].join('/')}` : undefined);
</script>

<div class="relative flex flex-row items-center">
	<Button
		variant="ghost"
		class="flex w-full flex-row items-center border-b py-5.5 text-sm"
		{href}
        onclick={onClick}
	>
		<div class="flex-2">
			<div class="flex flex-row items-center gap-2">
				{#if item.type === 'directory'}
					<Folder class="size-5" />
				{:else}
					<File class="size-5" />
				{/if}
				<span class="font-medium">{item.name}</span>
			</div>
		</div>
		<div class="text-muted-foreground flex w-50 items-center justify-start pl-10.5 text-sm">
			{formatBytes(item.size)}
		</div>
		<div class="text-muted-foreground flex w-60 items-center justify-start pl-8.5 text-sm">
			{new Date(item.lastModified).toLocaleDateString('en-US', {
				month: 'short',
				day: 'numeric',
				year: 'numeric'
			})}
		</div>
	</Button>
	<StorageItemActions {mode} {item} {onRestore} {onDelete} {onDownload} {onRename} {onInfo} {onRecycleBin} />
</div>
