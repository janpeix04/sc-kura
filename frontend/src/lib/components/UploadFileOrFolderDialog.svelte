<script lang="ts">
	import { enhance } from '$app/forms';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import Button from './ui/button/button.svelte';
	import { CloudUpload, CircleCheckBig } from '@lucide/svelte';
	import { ScrollArea } from './ui/scroll-area';
	import { Separator } from './ui/separator';

	let { dialogOpen = $bindable() }: { dialogOpen: boolean } = $props();

	let fileInput: HTMLInputElement | undefined = $state();
	let folderInput: HTMLInputElement | undefined = $state();
	let selectedFiles: File[] = $state([]);

    let isDragging = $state(false);

	function handleChange(event: Event) {
		const input = event.target as HTMLInputElement;
		if (!input.files) return;

		selectedFiles = [...selectedFiles, ...Array.from(input.files)];
	}

    function handleDragOver(event: DragEvent) {
        event.preventDefault();
        isDragging = true;
    }

    function handleDragLeave(event: DragEvent) {
        event.preventDefault();
        isDragging = false;
    }

	function handleDrop(event: DragEvent) {
		event.preventDefault();
        isDragging = false;

		if (!event.dataTransfer) return;

		const items = event.dataTransfer.items;
		const files: File[] = [];

		const traverseFileTree = (item: FileSystemEntry, path = '') => {
			if (item.isFile) {
                const fileEntry = item as FileSystemFileEntry;
				fileEntry.file((file: File) => {
					file = new File([file], path + file.name, { type: file.type });
					files.push(file);
				});
			} else if (item.isDirectory) {
                const directoryEntry = item as FileSystemDirectoryEntry;
				const dirReader = directoryEntry.createReader();
				dirReader.readEntries((entries: FileSystemEntry[]) => {
					entries.forEach((entry) => traverseFileTree(entry, path + item.name + '/'));
				});
			}
		};

		for (let i = 0; i < items.length; i++) {
			const item = items[i].webkitGetAsEntry();
			if (item) traverseFileTree(item);
		}

		setTimeout(() => {
			selectedFiles = [...selectedFiles, ...files];
		}, 100);
	}

	function reset() {
		selectedFiles = [];
		fileInput = undefined;
		folderInput = undefined;
		dialogOpen = false;
	}
</script>

<Dialog.Root bind:open={dialogOpen}>
	<Dialog.Content showCloseButton={false}>
		<Dialog.Header>
			<Dialog.Title class="text-center">Upload</Dialog.Title>
		</Dialog.Header>
		<form
			action="?/uploadFiles"
			method="POST"
            enctype="multipart/form-data"
			class="flex flex-col gap-4"
			use:enhance={({ formData }) => {
				selectedFiles.forEach((file) => formData.append('files', file));
				dialogOpen = false;
			}}
		>
			<div
				class={`text-muted-foreground flex h-64 flex-col items-center justify-center border-2 border-dashed p-6 text-center ${isDragging ? 'border-primary': 'border-muted-foreground'}`}
				ondrop={handleDrop}
                ondragover={handleDragOver}
                ondragleave={handleDragLeave}
				role="region"
				aria-label="File drop zone"
			>
				{#if selectedFiles.length === 0}
					<CloudUpload class={`size-16 ${isDragging ? 'text-primary': 'text-muted-foreground'}`} />
					Drag files or folders here
				{:else}
					<CircleCheckBig class="text-semantic-success size-16" />
					<span>{selectedFiles.length} file(s) selected</span>
				{/if}
			</div>
			{#if selectedFiles.length === 0}
				<div
					class="absolute bottom-24 left-1/2 z-10 flex -translate-x-1/2 flex-row items-center justify-center gap-2"
				>
					<Button class="cursor-pointer" onclick={() => fileInput?.click()}>File</Button>
					<Button class="cursor-pointer" onclick={() => folderInput?.click()}>Folder</Button>

					<input
						bind:this={folderInput}
						onchange={handleChange}
						class="hidden"
						type="file"
						multiple
						webkitdirectory
					/>
					<input
						bind:this={fileInput}
						onchange={handleChange}
						class="hidden"
						type="file"
						multiple
					/>
				</div>
			{:else}
				<ScrollArea class="max-h-40 rounded-md border">
					<div class=" mt-2">
						{#each selectedFiles as file, idx (idx)}
							<div class="px-4 text-sm">
								{file.name}
							</div>
							{#if idx !== selectedFiles.length - 1}
								<Separator class="my-2" />
							{:else}
								<div class="mb-2"></div>
							{/if}
						{/each}
					</div>
				</ScrollArea>
			{/if}

			<div class="flex justify-end gap-2">
				<Button variant="outline" onclick={reset}>Cancel</Button>
				<Button type="submit">Upload</Button>
			</div>
		</form>
	</Dialog.Content>
</Dialog.Root>
