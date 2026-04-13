import type { CeleryTaskResponse } from '$lib/client';
import { toast } from 'svelte-sonner';
import { get, writable, type Writable } from 'svelte/store';
import { getStatus } from './utils';
import type { CeleryResult } from '$lib/schemas/types';

/**
 * Task states enum
 */
export const TASK_STATES = Object.freeze({
	//: Task state is unknown (assumed pending since you know the id).
	PENDING: 'PENDING',
	//: Task was received by a worker (only used in events).
	RECEIVED: 'RECEIVED',
	//: Task was started by a worker (:setting:`task_track_started`).
	STARTED: 'STARTED',
	//: Task succeeded
	SUCCESS: 'SUCCESS',
	//: Task failed
	FAILURE: 'FAILURE',
	//: Task was revoked.
	REVOKED: 'REVOKED',
	//: Task was rejected (only used in events).
	REJECTED: 'REJECTED',
	//: Task is waiting for retry.
	RETRY: 'RETRY',
	IGNORED: 'IGNORED'
});

export const TASK_GROUPS = Object.freeze({
	READY_STATES: new Set<TaskState>([TASK_STATES.SUCCESS, TASK_STATES.FAILURE, TASK_STATES.REVOKED]),
	UNREADY_STATES: new Set<TaskState>([
		TASK_STATES.PENDING,
		TASK_STATES.RECEIVED,
		TASK_STATES.STARTED,
		TASK_STATES.RETRY
	]),
	EXCEPTION_STATES: new Set<TaskState>([
		TASK_STATES.RETRY,
		TASK_STATES.FAILURE,
		TASK_STATES.REVOKED
	])
});

export type TaskState = (typeof TASK_STATES)[keyof typeof TASK_STATES];

export const REQUEST_STATUS = {
	IDLE: 'idle',
	LOADING: 'loading',
	SUCCESS: 'success',
	ERROR: 'error'
} as const;

export type RequestStatus = (typeof REQUEST_STATUS)[keyof typeof REQUEST_STATUS];

export interface RequestOptions<T = unknown> {
	handleUpdate?: (data: T) => void;
	onProgress?: (progress: number) => void;
	signal?: AbortSignal;
	toastOnError?: boolean;
}

export interface RequestState {
	progress: number;
	status: RequestStatus;
	error: string | undefined;
}

export function createRequestState(): RequestState {
	return {
		progress: 0,
		status: REQUEST_STATUS.IDLE,
		error: undefined
	};
}

function isTaskReady(state: TaskState): boolean {
	return TASK_GROUPS.READY_STATES.has(state);
}

function isTaskFailed(state: TaskState): boolean {
	return TASK_GROUPS.EXCEPTION_STATES.has(state);
}

function getTaskErrorMessage(taskData: CeleryTaskResponse) {
	let errorMessage = `Task failed with state: ${taskData.state}`;
	if (typeof taskData.details === 'string') {
		errorMessage = taskData.details;
	} else if (typeof taskData.details?.error === 'string') {
		errorMessage = taskData.details?.error;
	}
	return errorMessage;
}

/**
 * Poll a task status until completed
 */
async function pollTask<T = unknown>(
	initialTaskData: CeleryTaskResponse,
	statusChecker: (taskId: string) => Promise<CeleryTaskResponse>,
	options: RequestOptions<T> = {}
): Promise<T> {
	const { handleUpdate, onProgress, signal, toastOnError } = options;
	let taskData = initialTaskData;

	while (!isTaskReady(taskData.state as TaskState)) {
		if (signal?.aborted) throw new Error('Cancelled');

		if (handleUpdate && taskData.details) {
			handleUpdate(taskData.details as T);
		}
		if (onProgress && taskData.progress) {
			onProgress(taskData.progress);
		}

		await new Promise((resolve, reject) => {
			const timer = setTimeout(resolve, 500);
			if (signal) {
				signal.addEventListener(
					'abort',
					() => {
						clearTimeout(timer);
						reject(new Error('Cancelled'));
					},
					{ once: true }
				);
			}
		});

		taskData = await statusChecker(taskData.task_id);
	}

	if (taskData.state === TASK_STATES.SUCCESS) {
		return taskData.details as T;
	} else {
		const errorMessage = getTaskErrorMessage(taskData);
		if (toastOnError) toast.error(errorMessage);
		throw new Error(errorMessage);
	}
}

type StateUpdater = {
	get(): RequestState;
	set(state: Partial<RequestState>): void;
};

function createStateUpdater(state: RequestState | Writable<RequestState>): StateUpdater {
	if (typeof (state as Writable<RequestState>).subscribe === 'function') {
		return {
			get: () => get(state as Writable<RequestState>),
			set: (partial) => {
				const current = get(state as Writable<RequestState>);
				(state as Writable<RequestState>).set({ ...current, ...partial });
			}
		};
	} else {
		return {
			get: () => state as RequestState,
			set: (partial) => Object.assign(state as RequestState, partial)
		};
	}
}

/**
 * Handle a request with reactive state updates.
 *
 * Supports both plain object and Svelte store for `state`.
 * Automatically sets progress, status, and handles polling of async tasks.
 *
 * @template T - The expected return type of the task.
 * @param requestFn - A function that starts the async task and returns a CeleryTaskResponse.
 * @param statusChecker - A function to check the task's status by ID.
 * @param state - Either a writable Svelte store or a plain RequestState object.
 * @param options - Optional config for update callbacks and abort signals.
 * @returns A promise that resolves with the task result of type T.
 */
export async function handleRequest<T = unknown>(
	requestFn: () => Promise<CeleryTaskResponse>,
	statusChecker: (taskId: string) => Promise<CeleryTaskResponse>,
	state: RequestState | Writable<RequestState>,
	options: RequestOptions<T> = {}
): Promise<T> {
	const { handleUpdate, signal, toastOnError } = options;
	const stateUpdater = createStateUpdater(state);

	stateUpdater.set({ progress: 0, error: undefined });

	const response = await requestFn();

	if (response.state === TASK_STATES.SUCCESS) {
		stateUpdater.set({ status: REQUEST_STATUS.SUCCESS, progress: 100 });
		return response.details as T;
	}

	if (isTaskFailed(response.state as TaskState)) {
		const errorMessage = getTaskErrorMessage(response);
		if (toastOnError) toast.error(errorMessage);
		throw new Error(errorMessage);
	}

	stateUpdater.set({ status: REQUEST_STATUS.LOADING });

	const result = await pollTask<T>(response, statusChecker, {
		handleUpdate,
		onProgress: (progress) => {
			stateUpdater.set({ progress });
		},
		signal,
		toastOnError
	});

	stateUpdater.set({ progress: 100, status: REQUEST_STATUS.SUCCESS });

	return result;
}

export const requestState = writable(createRequestState());

function handleResult(result: CeleryResult) {
	if (result.errors.length > 0) {
		toast.error(result.errors.join(', '));
		/* ErrorToast, {
			componentProps: {
				errors: result.errors,
				noSuccessCount: result.total_count - result.success_count,
				totalCount: result.total_count
			},
			duration: Infinity,
			closeButton: true
		} */
	}
	if (result.success_count > 0) {
		toast.success(result.message);
	}
}

export function showToastAndHandleRequest({
	celeryResponse,
	size,
	toastId,
	reset
}: {
	celeryResponse: CeleryTaskResponse;
	size: number;
	toastId: string;
	reset?: () => void;
}) {
	toast.loading(`Processing ${size} file${size > 1 ? 's' : ''}...`, {
		id: toastId,
		duration: Infinity,
		closeButton: true
	});

	/* ProgressToast, {
		componentProps: { size },
		id: toastId,
		duration: Infinity
	} */

	handleRequest(
		() =>
			Promise.resolve({
				task_id: celeryResponse.task_id,
				state: celeryResponse.state,
				progress: celeryResponse.progress,
				details: celeryResponse.details,
				total: celeryResponse.total
			}),
		getStatus,
		requestState
	).then((result) => {
		requestState.set(createRequestState());
		handleResult(result as CeleryResult);
		toast.dismiss(toastId);
		if (reset) reset();
	});
}
