<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import type { FilePublic, FolderPublic } from '$lib/client';

	let {
		folders = $bindable(),
		files = $bindable()
	}: {
		folders?: FolderPublic[];
		files?: FilePublic[];
	} = $props();

	let sortKey = $state<'name' | 'owner' | 'date_modified' | 'size'>('name');
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
</script>

<div class="contents cursor-pointer font-semibold">
	<div
		role="button"
		class="justify-start rounded-t-lg border-b border-b-border px-2 py-2 text-base font-medium hover:bg-background"
		onclick={() => toggleSort('name')}
		onkeydown={(e) => e.key === 'Enter' && toggleSort('name')}
		tabindex="0"
	>
		{m.name()}
	</div>
	<div
		role="button"
		class="justify-start rounded-t-lg border-b border-b-border px-2 py-2 text-base font-medium hover:bg-background"
		onclick={() => toggleSort('owner')}
		onkeydown={(e) => e.key === 'Enter' && toggleSort('owner')}
		tabindex="0"
	>
		{m.owner()}
	</div>
	<div
		role="button"
		class="justify-start rounded-t-lg border-b border-b-border px-2 py-2 text-base font-medium hover:bg-background"
		onclick={() => toggleSort('date_modified')}
		onkeydown={(e) => e.key === 'Enter' && toggleSort('date_modified')}
		tabindex="0"
	>
		{m.modified()}
	</div>
	<div
		role="button"
		class="justify-start rounded-t-lg border-b border-b-border px-2 py-2 text-base font-medium hover:bg-background"
		onclick={() => toggleSort('size')}
		onkeydown={(e) => e.key === 'Enter' && toggleSort('size')}
		tabindex="0"
	>
		{m.size()}
	</div>
	<div class="justify-start border-b border-b-border px-2 py-2 text-base font-medium"></div>
</div>
