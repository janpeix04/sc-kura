<script lang="ts">
	import { usersMeGet } from "$lib/client";
	import { createClient } from "$lib/client/client";
	import { onMount } from "svelte";

    const client = createClient({ baseUrl: ''});
    let data = $state()
    onMount(async () => {
        const { data: user } = await usersMeGet({
            client,
            throwOnError: true
        });
        data = user
    })
</script>

<div>
    USER: {data}
</div>