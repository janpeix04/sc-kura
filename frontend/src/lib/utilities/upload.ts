export const MAX_SIZE = 10 * 1024 * 1024;
export const CHUNK_SIZE = 5 * 1024 * 1024;

export async function uploadFile(file: File, parentId: string) {
	if (file.size < MAX_SIZE) {
		return uploadDirect(file, parentId);
	} else {
		uploadChunked(file, parentId);
	}
}

export async function uploadFiles(files: FileList, parentId: string) {
    const uploads = [];

    for (const file of files) {
        uploads.push(uploadFile(file, parentId));
    }

    return Promise.all(uploads);
}

async function uploadDirect(file: File, parentId: string) {
    const formData = new FormData();
    
    /* TODO: Upload file endpoint */
}

async function uploadChunked(file: File, parentId: string) {
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    const uploadId = crypto.randomUUID();

    for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);

        const chunk = file.slice(start, end);

        /* TODO: Upload chunks endpoint */
    }

    /* TODO: Upload complete endpoint */
}
