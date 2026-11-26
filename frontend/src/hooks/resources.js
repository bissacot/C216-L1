import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

// The key identifies the complete request, including path and applied filters.
export function useResource(key, load, interval = 0) {
  const loader = useRef(load);
  loader.current = load;
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState({});
  const refresh = useCallback(() => setRevision((v) => v + 1), []);
  useEffect(() => {
    const controller = new AbortController();
    let timer;
    async function run() {
      if (!document.hidden || !interval || !timer) {
        setState((s) =>
          s.key === key ? { ...s, loading: true } : { key, loading: true },
        );
        try {
          const data = await loader.current(controller.signal);
          if (!controller.signal.aborted)
            setState({ key, revision, data, loading: false });
        } catch (error) {
          if (!controller.signal.aborted)
            setState((s) => ({
              ...s,
              key,
              revision,
              error: error.message,
              loading: false,
            }));
        }
      }
      if (interval && !controller.signal.aborted)
        timer = setTimeout(run, interval);
    }
    run();
    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [key, revision, interval]);
  return {
    ...(state.key === key ? state : {}),
    loading: state.key !== key || state.revision !== revision || state.loading,
    refresh,
  };
}

export function useAction() {
  const lock = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function run(action, onSuccess, onError) {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      const result = await action();
      onSuccess?.(result);
    } catch (e) {
      setError(onError?.(e) || e.message);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return { busy, error, run, clear: () => setError("") };
}

export function useList(defaults = {}) {
  const [search, setSearch] = useSearchParams();
  const values = { ...defaults, ...Object.fromEntries(search) };
  const page = Math.max(1, Number.parseInt(values.page, 10) || 1);
  function apply(next) {
    const query = new URLSearchParams();
    for (const [k, v] of Object.entries(next))
      if (v !== "" && v != null) query.set(k, v);
    setSearch(query);
  }
  return {
    values,
    page,
    apply,
    go: (p) => apply({ ...values, page: p }),
    key: search.toString(),
  };
}
