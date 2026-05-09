import type { MouseEventHandler, ReactNode } from "react";
import { createPortal } from "react-dom";

interface ModalProps{
    children: ReactNode,
    closeModal: () => void
}

export function ModalWrapper({ children, closeModal }: ModalProps) {
  const modalRoot = document.getElementById("modal-root");
  if (modalRoot == null) {
    console.error("no modal root found");
    return null;
  }

  const handleBgClick: MouseEventHandler<HTMLDivElement> = (e) => {
    e.stopPropagation();
    closeModal();
  };

  return createPortal(
    // darkened background wrapper
    <div className="modal-wrapper" onClick={handleBgClick} id="modal"> 
      {children}
    </div>,
    modalRoot // portal destination
  );

}
