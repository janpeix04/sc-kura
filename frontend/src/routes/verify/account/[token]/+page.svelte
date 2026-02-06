<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    let { data } = $props();
</script>

<div class="w-full h-full bg-primary flex items-center justify-center">
    <div 
        class="bg-secondary w-105 rounded-3xl px-10 py-6" 
    >
        <div class="text-center mb-8">
            <h2 class="font-semibold text-xl">Account Verification</h2>
        </div>
        <div>
            {#if data.success}
                <p>{data.success}</p>
                <Button href='/login' class="w-full mt-4 h-11 px-2.5">Proceed to Log in</Button>
            {:else}
                <p>{data.error}</p>
           {/if}
        </div>
    </div>
</div>