<script lang="ts">
	import AppSidebar from "$lib/components/AppSidebar.svelte";
    import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { availableSpace } from "$lib/stores/storage.js";
	import { onMount } from "svelte";

    let { data, children } = $props();

    onMount(() => {
        availableSpace.set(data.availableSpace);
    })
</script>

<AppSidebar user={data.user} />
<Sidebar.Inset class="flex flex-1 flex-col overflow-hidden">
    {@render children()}
</Sidebar.Inset>