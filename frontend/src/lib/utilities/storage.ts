export function formatBytes(bytes: number, decimals: number = 2): string {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    const value = bytes / Math.pow(k, i);

    return `${value.toFixed(decimals)} ${sizes[i]}`;
}

export function get_path(segments: string[]) {
    return segments.length === 0 ? '/' : `/${segments.join('/')}`;
}