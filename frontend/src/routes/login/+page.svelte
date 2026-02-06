<script>
	import { ORIGINS } from '$lib/schemas/types.js';
	import { toast } from 'svelte-sonner';

    let { data } = $props();
    $effect(() => {
        if (data.origin === ORIGINS.Signup) {
            toast.info(data.message, {duration: 8000});
        }
    })
</script>

<div>
    dsdsd
</div>