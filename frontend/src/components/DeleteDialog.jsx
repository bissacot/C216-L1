import { useEffect, useRef } from "react";

export default function DeleteDialog({ aluno, onConfirm, onCancel }) {
  const dialogRef = useRef(null);
  const triggerRef = useRef(document.activeElement);
  useEffect(() => {
    const dialog = dialogRef.current;
    dialog.showModal();
    return () => {
      dialog.close();
      if (triggerRef.current?.isConnected) triggerRef.current.focus();
    };
  }, []);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="delete-title"
      aria-describedby="delete-description"
      onCancel={onCancel}
      className="fixed inset-0 m-auto w-[calc(100%-2rem)] max-w-md rounded-2xl border border-stone-200 bg-white p-7 text-stone-800 shadow-xl backdrop:bg-stone-950/40"
    >
      <h2 id="delete-title" className="text-xl font-semibold">
        Excluir aluno?
      </h2>
      <p
        id="delete-description"
        className="mt-3 break-words text-sm leading-6 text-stone-600"
      >
        O cadastro de <strong>{aluno.nome}</strong> será removido da lista. Esta
        ação não pode ser desfeita.
      </p>
      <div className="mt-6 flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-stone-300 px-4 py-2.5 text-sm font-medium hover:bg-stone-100"
        >
          Cancelar
        </button>
        <button
          type="button"
          onClick={onConfirm}
          className="rounded-lg bg-red-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-800"
        >
          Confirmar exclusão
        </button>
      </div>
    </dialog>
  );
}
