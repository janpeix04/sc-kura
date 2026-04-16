<script lang="ts">
	import { storageSearchGet, type FilePublic, type FolderPublic } from '$lib/client';
	import { m } from '$lib/paraglide/messages';
	import { clientSideClient } from '$lib/utilities/client-side';

	let query: string = $state('');
	let open = $state(false);
	let loading = $state(false);

	let folders: FolderPublic[] = $state([]);
	let files: FilePublic[] = $state([]);

	let timeout: ReturnType<typeof setTimeout>;
	let blurTimeout: ReturnType<typeof setTimeout>;
	let controller: AbortController;

	async function search(q: string) {
		if (!q.trim()) {
			open = false;
			folders = [];
			files = [];
			return;
		}

		loading = true;
		open = true;

		controller?.abort();
		controller = new AbortController();

		const { data } = await storageSearchGet({
			client: clientSideClient,
			query: {
				q
			},
			throwOnError: true
		});

		folders = data.folders;
		files = data.files;

		loading = false;
	}

	function onInput(e: Event) {
		const value = (e.target as HTMLInputElement).value;
		query = value;

		clearTimeout(timeout);

		timeout = setTimeout(() => {
			search(query);
		}, 300);
	}

	function resetSearch() {
		open = false;
		query = '';
		folders = [];
		files = [];
		loading = false;
		controller?.abort();
	}

	function onBlur() {
		blurTimeout = setTimeout(() => {
			resetSearch();
		}, 200);
	}

	function onFocus() {
		clearTimeout(blurTimeout);
		open = true;
	}
</script>

<div class="z-50 h-12 w-full px-12">
	<form
		class="flex items-center gap-2 {open && query
			? 'rounded-lg'
			: 'rounded-full'} bg-search-background p-1 transition-colors duration-300 ease-in-out focus-within:bg-white focus-within:shadow-sm"
	>
		<div class="flex w-full flex-col">
			<div class="flex items-center gap-2">
				<span class="ml-4 icon-[lucide--search] size-6"></span>
				<input
					class="w-full border-none bg-transparent outline-none focus:ring-0 focus:outline-none focus-visible:ring-0"
					type="text"
					placeholder={m.search_in_kura()}
					bind:value={query}
					oninput={onInput}
					onfocus={onFocus}
					onblur={onBlur}
				/>
			</div>

			{#if open && query}
				<div class="w-full overflow-auto">
					{#if loading}
						<div class="p-4 text-sm text-gray-500">{m.searching()}</div>
					{:else if folders.length === 0 && files.length === 0}
						<div class="p-4 text-sm text-gray-500">{m.no_results_found()}</div>
					{:else}
						{#if folders.length}
							<div class="p-2 text-xs font-semibold text-gray-400">{m.folders()}</div>
							{#each folders as folder (folder.id)}
								<a
									href={`/folder/${folder.id}`}
									class="flex items-center gap-2 px-4 py-2 hover:bg-gray-100"
								>
									<span class="icon-[lucide--folder] size-4"></span>
									{folder.name}
								</a>
							{/each}
						{/if}
						{#if files.length}
							<div class="p-2 text-xs font-semibold text-gray-400">{m.files()}</div>
							{#each files as file (file.id)}
								<a
									href={`/folder/${file.parent_id}`}
									class="flex items-center gap-2 px-4 py-2 hover:bg-gray-100"
								>
									<span class="icon-[lucide--file] size-4"></span>
									{file.name}
								</a>
							{/each}
						{/if}
					{/if}
				</div>
			{/if}
		</div>
	</form>
</div>
