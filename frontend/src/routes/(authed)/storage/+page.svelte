<script lang="ts">
	import UploadButton from '$lib/components/UploadButton.svelte';
</script>

<div class="flex h-full w-full bg-tertiary-foreground">
  <aside class="bg-tertiary-foreground w-64 h-full flex flex-col items-center py-6 gap-4">
    <UploadButton />
  </aside>

  <main class="flex-1 p-6 flex flex-col gap-4 overflow-auto">
    <div class="flex-1 bg-white rounded-lg shadow p-4 flex flex-col gap-4">
    </div>
  </main>
</div>
